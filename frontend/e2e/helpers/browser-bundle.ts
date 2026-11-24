import { mkdtemp, writeFile, readFile, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import path from "node:path";
export async function browserBundle(source: string) {
  const directory = await mkdtemp(path.join(tmpdir(), "cumpleia-acceptance-ui-"));
  try {
    const loader = path.join(directory, "typescript-loader.cjs");
    await writeFile(
      loader,
      `const ts=require(${JSON.stringify(require.resolve("typescript"))});module.exports=function(source){return ts.transpileModule(source,{compilerOptions:{module:ts.ModuleKind.ESNext,target:ts.ScriptTarget.ES2021,jsx:ts.JsxEmit.ReactJSX}}).outputText};`
    );
    const entry = path.join(directory, "entry.js");
    await writeFile(entry, source);
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
            alias: { "@": process.cwd() },
            modules: [path.resolve("node_modules"), "node_modules"],
          },
          module: { rules: [{ test: /\.tsx?$/, use: loader }] },
          plugins: [
            new runtime.webpack.DefinePlugin({
              "process.env.NEXT_PUBLIC_API_URL": JSON.stringify("http://test.invalid"),
            }),
          ],
        },
        (error: Error | null, stats: { hasErrors: () => boolean; toString: () => string }) =>
          error || stats.hasErrors() ? reject(error ?? new Error(stats.toString())) : resolve()
      )
    );
    return await readFile(path.join(directory, "bundle.js"), "utf8");
  } finally {
    await rm(directory, { recursive: true, force: true });
  }
}
