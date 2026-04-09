import type { MetadataRoute } from "next";

const baseUrl = "https://gscompanion.example.com";

export default function sitemap(): MetadataRoute.Sitemap {
  const routes = [
    "",
    "/search",
    "/units",
    "/equips",
    "/tierlists",
    "/bosses",
    "/comps",
    "/team-builder",
    "/modes",
    "/guides",
    "/ai-presets",
    "/progression",
    "/admin",
  ];

  return routes.map((route) => ({
    url: `${baseUrl}${route}`,
    lastModified: new Date(),
    changeFrequency: "daily",
    priority: route === "" ? 1 : 0.7,
  }));
}
