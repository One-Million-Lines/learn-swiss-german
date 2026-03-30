import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";
import tailwindcss from "@tailwindcss/vite";
import path from "path";
import fs from "fs";

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => ({
  base: mode === "production" ? "/demo/learn-swiss-german/" : "/",
  server: {
    host: "::",
    port: 5306,
  },
  plugins: [
    react(),
    tailwindcss(),
    {
      name: "serve-data-json",
      configureServer(server) {
        server.middlewares.use("/data", (req, res, next) => {
          const filePath = path.join(__dirname, "data-json", req.url!);
          if (fs.existsSync(filePath) && fs.statSync(filePath).isFile()) {
            res.setHeader("Content-Type", "application/json");
            fs.createReadStream(filePath).pipe(res);
          } else {
            next();
          }
        });
      },
    },
  ],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
}));
