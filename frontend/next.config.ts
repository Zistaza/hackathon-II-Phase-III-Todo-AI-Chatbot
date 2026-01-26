import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  experimental: {
    serverActions: true,
  },
  env: {},
  images: {
    domains: ['localhost', '127.0.0.1'],
  },
};

export default nextConfig;
