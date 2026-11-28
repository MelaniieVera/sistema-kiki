import type { NextConfig } from "next";

const apiOrigin = process.env.KIKI_API_ORIGIN ?? "http://127.0.0.1:8000";

const nextConfig: NextConfig = {
  async rewrites() {
    return [{
      source: "/api/kiki/:path*",
      destination: `${apiOrigin.replace(/\/$/, "")}/api/v1/:path*`,
    }];
  },
};

export default nextConfig;
