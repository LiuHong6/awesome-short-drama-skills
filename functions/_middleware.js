// 访问日志：每个页面请求写一行到 Workers Analytics Engine（绑定名 CRAWL_LOG，数据集 shortdrama_crawl）。
// 爬虫记 UA、IP 和 ASN，用来对照各家公布的 IP 段验真；真人只记页面、来源网站、utm_source 和国家，不记 IP、不放 cookie。
// 没绑定数据集或写入出错时照常返回页面。/static/* 不经过这里（见 web/_routes.json）。
// 字段顺序由 ~/openclaw/products/geoseo 的 collect.py 读取，改动要两边一起改。

// [UA 里的名字, 公司, 类别]。类别：search 搜索索引；train 训练；user 用户提问时 AI 来读页面。先匹配的先算。
const BOTS = [
  ["ChatGPT-User", "openai", "user"], ["OAI-SearchBot", "openai", "search"], ["GPTBot", "openai", "train"],
  ["Claude-User", "anthropic", "user"], ["Claude-SearchBot", "anthropic", "search"], ["ClaudeBot", "anthropic", "train"],
  ["Perplexity-User", "perplexity", "user"], ["PerplexityBot", "perplexity", "search"],
  ["Kimi-User", "moonshot", "user"], ["Kimi-SearchBot", "moonshot", "search"], ["KimiBot", "moonshot", "train"],
  ["MistralAI-User", "mistral", "user"], ["DuckAssistBot", "duckduckgo", "user"], ["meta-externalfetcher", "meta", "user"],
  ["Google-Agent", "google", "user"], ["Googlebot", "google", "search"], ["Google-InspectionTool", "google", "search"],
  ["bingbot", "microsoft", "search"], ["Applebot", "apple", "search"],
  ["Baiduspider", "baidu", "search"], ["YisouSpider", "alibaba", "search"], ["Sogou", "sogou", "search"],
  ["360Spider", "qihoo", "search"], ["PetalBot", "huawei", "search"], ["YandexBot", "yandex", "search"],
  ["DuckDuckBot", "duckduckgo", "search"],
  ["Bytespider", "bytedance", "train"], ["meta-externalagent", "meta", "train"], ["CCBot", "commoncrawl", "train"],
  ["Amazonbot", "amazon", "train"],
];
const OTHER_BOT = /bot|crawl|spider|slurp|fetch|scrap|curl|wget|python|httpx|go-http|java\/|headless|preview/i;

// 和 web/_headers 一致。_headers 不一定作用于经过 Functions 的响应，这里补上。
const HEADERS = { "X-Content-Type-Options": "nosniff", "Referrer-Policy": "strict-origin-when-cross-origin" };

function classify(ua) {
  for (const [token, family, category] of BOTS) {
    if (ua.includes(token)) return { kind: "bot", token, family, category };
  }
  if (OTHER_BOT.test(ua)) return { kind: "bot", token: "", family: "other", category: "other" };
  return { kind: "human", token: "", family: "", category: "" };
}

function refHost(ref, host) {
  try {
    const h = new URL(ref).hostname;
    return h === host ? "" : h;
  } catch {
    return "";
  }
}

export async function onRequest(context) {
  const { request, env } = context;
  let res = await context.next();
  res = new Response(res.body, res);
  for (const [k, v] of Object.entries(HEADERS)) if (!res.headers.has(k)) res.headers.set(k, v);
  const url = new URL(request.url);
  if (url.pathname === "/data.json" && !res.headers.has("Access-Control-Allow-Origin")) {
    res.headers.set("Access-Control-Allow-Origin", "*");
  }

  try {
    if (env.CRAWL_LOG) {
      const ua = request.headers.get("User-Agent") || "";
      const c = classify(ua);
      const bot = c.kind === "bot";
      const cf = request.cf || {};
      env.CRAWL_LOG.writeDataPoint({
        indexes: [url.hostname],
        blobs: [
          c.kind, c.family, c.category, url.pathname.slice(0, 300), String(res.status),
          bot ? "" : refHost(request.headers.get("Referer") || "", url.hostname),
          bot ? "" : (url.searchParams.get("utm_source") || "").slice(0, 100),
          cf.country || "",
          bot ? ua.slice(0, 300) : "",
          bot ? request.headers.get("CF-Connecting-IP") || "" : "",
          bot ? String(cf.asn || "") : "",
          c.token,
        ],
        doubles: [res.status],
      });
    }
  } catch (e) {
    // 日志失败不影响页面
  }
  return res;
}
