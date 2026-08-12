import type { NextConfig } from "next";

const pagesPath = process.env.GITHUB_ACTIONS ? "/pet-saude-sinais" : "";

const nextConfig: NextConfig = {
  output: "export",
  basePath: pagesPath,
  trailingSlash: true,
  images: {
    unoptimized: true
  },
  turbopack: {
    root: process.cwd()
  }
};

export default nextConfig;
