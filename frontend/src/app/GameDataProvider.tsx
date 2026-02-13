"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useRef,
  useState,
} from "react";
import type { Game, ConnectionStatus } from "./types";

const BACKEND_URL = "pj09-sports-betting.onrender.com";
const WS_URL = `wss://${BACKEND_URL}/ws`;
const API_URL = `https://${BACKEND_URL}/api/games`;
const RECONNECT_INTERVAL = 5000; // 5 second interval
const MAX_RECONNECT_ATTEMPTS = 10;

type GameDataContextValue = {
  games: Game[];
  status: ConnectionStatus;
  error: string | null;
  reconnect: () => void;
};

const GameDataContext = createContext<GameDataContextValue | null>(null);

export function GameDataProvider({ children }: { children: React.ReactNode }) {
  const [games, setGames] = useState<Game[]>([]);
  const [status, setStatus] = useState<ConnectionStatus>("connecting");
  const [error, setError] = useState<string | null>(null);

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectAttemptsRef = useRef(0);

  // used for initial data population
  const fetchGames = useCallback(async () => {
    try {
      const res = await fetch(API_URL);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      setGames(Array.isArray(data) ? data : (data?.games ?? []));
    } catch (e) {
      console.error("Fetch games failed:", e);
      setError("Failed to fetch games");
    }
  }, []);

  const connect = useCallback(() => {
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

        if (reconnectAttemptsRef.current < MAX_RECONNECT_ATTEMPTS) {
          reconnectAttemptsRef.current += 1;
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
  }, []);

  const reconnect = useCallback(() => {
    reconnectAttemptsRef.current = 0;
    if (wsRef.current) {
      wsRef.current.close();
    }
    connect();
  }, [connect]);

  useEffect(() => {
    fetchGames();
  }, [fetchGames]);

  useEffect(() => {
    connect();

    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [connect]);

  const value: GameDataContextValue = {
    games,
    status,
    error,
    reconnect,
  };

  return (
    <GameDataContext.Provider value={value}>
      {children}
    </GameDataContext.Provider>
  );
}

export function useGameData(): GameDataContextValue {
  const ctx = useContext(GameDataContext);
  if (!ctx) {
    throw new Error("useGameData must be used within GameDataProvider");
  }
  return ctx;
}
