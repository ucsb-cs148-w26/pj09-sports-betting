"use client";

import { useEffect, useState, useRef } from "react";
import type { Game, ConnectionStatus } from "./types";


const BACKEND_URL = "pj09-sports-betting.onrender.com";
const WS_URL = `wss://${BACKEND_URL}/ws`;
const API_URL = `https://${BACKEND_URL}/api/games`;
const RECONNECT_INTERVAL = 5000; // 5 second interval
const MAX_RECONNECT_ATTEMPTS = 10;

export function useGameData() {
  const [games, setGames] = useState<Game[]>([]);
  const [status, setStatus] = useState<ConnectionStatus>("connecting");
  const [error, setError] = useState<string | null>(null);

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectAttemptsRef = useRef(0);

  const fetchGames = async () => {
    try {
      const res = await fetch(API_URL);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      console.log("Fetched games:", data);
      setGames(Array.isArray(data) ? data : (data?.games ?? []));
    } catch (e) {
      console.error("Fetch games failed:", e);
      setError("Failed to fetch games");
    }
  };

  useEffect(() => {
    fetchGames();
  }, []);

  const connect = () => {
    try {
      setStatus("connecting");
      setError(null);

      const ws = new WebSocket(WS_URL);
      wsRef.current = ws;

      ws.onopen = () => {
        console.log("WebSocket connected");
        setStatus("connected");
        setError(null);
        reconnectAttemptsRef.current = 0;
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          setGames(data);
        } catch (err) {
          console.error("Failed to parse game data:", err);
          setError("Failed to parse game data");
        }
      };

      ws.onerror = (event) => {
        console.error("WebSocket error:", event);
        setStatus("error");
        setError("WebSocket connection error");
      };

      ws.onclose = () => {
        console.log("WebSocket disconnected");
        setStatus("disconnected");

        // Attempt to reconnect
        if (reconnectAttemptsRef.current < MAX_RECONNECT_ATTEMPTS) {
          reconnectAttemptsRef.current += 1;
          console.log(
            `Reconnecting... (attempt ${reconnectAttemptsRef.current})`,
          );

          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, RECONNECT_INTERVAL);
        } else {
          setError(
            "Max reconnection attempts reached. Backend may not be ready.",
          );
        }
      };
    } catch (err) {
      console.error("Failed to create WebSocket:", err);
      setStatus("error");
      setError("Failed to create WebSocket connection");
    }
  };

  const reconnect = () => {
    reconnectAttemptsRef.current = 0;
    connect();
  };

  useEffect(() => {
    connect();

    // Cleanup on unmount
    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  return { games, status, error, reconnect };
}
