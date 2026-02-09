import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "a1.espncdn.com",
      },
    ],
  },
};

export default nextConfig;
