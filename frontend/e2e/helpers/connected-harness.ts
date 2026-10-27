import { mkdtemp, readFile, writeFile } from "node:fs/promises";
import { execFileSync } from "node:child_process";
import { tmpdir } from "node:os";
import path from "node:path";
import type { OrganizationMembershipOut } from "../../lib/api/client";

export async function buildConnectedHarness(
  organizations: OrganizationMembershipOut[],
  apiUrl: string
) {
  const directory = await mkdtemp(path.join(tmpdir(), "cumpleia-connected-"));
  const loader = path.join(directory, "loader.cjs");
  await writeFile(
    loader,
    `const ts=require(${JSON.stringify(require.resolve("typescript"))});module.exports=source=>ts.transpileModule(source,{compilerOptions:{module:ts.ModuleKind.ESNext,target:ts.ScriptTarget.ES2021,jsx:ts.JsxEmit.ReactJSX}}).outputText;`
  );
  const auth = path.join(directory, "auth.js"),
    router = path.join(directory, "router.js"),
    link = path.join(directory, "link.js"),
    empty = path.join(directory, "empty.cjs");
  await writeFile(
    auth,
    'export const createClient=()=>({auth:{getSession:async()=>({data:{session:{access_token:"PRUEBA"}}}),signOut:async()=>({})}});'
  );
  await writeFile(
    router,
    'export const usePathname=()=>"/dashboard/trabajo";export const useRouter=()=>({push:()=>{},refresh:()=>{},replace:()=>{}});'
  );
  await writeFile(
    link,
    'import React from "react";export default function Link({prefetch,...props}){return React.createElement("a",props)};'
  );
  await writeFile(empty, 'module.exports=()=>"";');
  const entry = path.join(directory, "entry.js");
  await writeFile(
    entry,
    `import React from "react";import {createRoot} from "react-dom/client";import {ConnectedWorkspace} from ${JSON.stringify(path.resolve("components/navigation/ConnectedWorkspace.tsx"))};import {DashboardContent} from ${JSON.stringify(path.resolve("components/navigation/DashboardContent.tsx"))};createRoot(document.getElementById("root")).render(React.createElement("div",{className:"dashboard-shell"},React.createElement(DashboardContent,null,React.createElement(ConnectedWorkspace,{organizations:${JSON.stringify(organizations)}}))));`
  );
  const runtime = require("next/dist/compiled/webpack/webpack");
  runtime.init();
  await new Promise<void>((resolve, reject) =>
    runtime.webpack(
      {
        mode: "development",
        devtool: false,
        entry,
        output: { path: directory, filename: "bundle.js" },
        resolve: {
          extensions: [".ts", ".tsx", ".js"],
          alias: {
            "@/lib/supabase/client$": auth,
            "next/navigation$": router,
            "next/link$": link,
            "@": process.cwd(),
          },
          modules: [path.resolve("node_modules"), "node_modules"],
        },
        module: {
          rules: [
            { test: /\.tsx?$/, use: loader },
            { test: /\.css$/, use: empty },
          ],
        },
        plugins: [
          new runtime.webpack.DefinePlugin({
            "process.env.NEXT_PUBLIC_API_URL": JSON.stringify(apiUrl),
          }),
        ],
      },
      (error: Error | null, stats: { hasErrors: () => boolean; toString: () => string }) =>
        error || stats.hasErrors() ? reject(error ?? new Error(stats.toString())) : resolve()
    )
  );
  const script = await readFile(path.join(directory, "bundle.js"), "utf8");
  const source = path.join(directory, "tailwind.css");
  await writeFile(source, await readFile("app/globals.css", "utf8"));
  execFileSync(
    process.execPath,
    [
      require.resolve("tailwindcss/lib/cli.js"),
      "-i",
      source,
      "-o",
      path.join(directory, "style.css"),
      "--content",
      "components/**/*.tsx",
    ],
    { stdio: "pipe" }
  );
  const css =
    (await readFile(path.join(directory, "style.css"), "utf8")) +
    (await readFile("components/navigation/navigation-prototype.css", "utf8")) +
    (await readFile("components/navigation/connected-navigation.css", "utf8"));

  return { directory, script, css };
}
