import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  images: {
    // allow external team logos from ESPN CDN
    domains: ["a1.espncdn.com"],
  },
};

export default nextConfig;
