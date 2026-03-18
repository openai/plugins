// hooks/src/stemmer.mts
var EXCEPTIONS_ING = /* @__PURE__ */ new Set([
  "ring",
  "king",
  "thing",
  "string",
  "bring",
  "sing",
  "spring",
  "swing",
  "sting",
  "cling",
  "fling",
  "sling",
  "wring",
  "during",
  "ceiling",
  "being",
  "nothing",
  "something",
  "anything",
  "everything",
  "morning",
  "evening",
  "ping",
  "bing",
  "wing",
  "ding",
  "ming"
]);
var EXCEPTIONS_ED = /* @__PURE__ */ new Set([
  "bed",
  "red",
  "fed",
  "led",
  "shed",
  "wed",
  "sled",
  "bled",
  "bred",
  "fled",
  "shred",
  "sped",
  "need",
  "seed",
  "feed",
  "speed",
  "indeed"
]);
var EXCEPTIONS_TION = /* @__PURE__ */ new Set([
  "mention",
  "question",
  "caution",
  "portion",
  "section",
  "notion",
  "potion",
  "fashion",
  "bastion",
  "function",
  "junction",
  "auction"
]);
var EXCEPTIONS_MENT = /* @__PURE__ */ new Set([
  "element",
  "comment",
  "moment",
  "segment",
  "fragment",
  "garment",
  "cement",
  "ament",
  "torment",
  "ferment",
  "lament"
]);
var EXCEPTIONS_LY = /* @__PURE__ */ new Set([
  "only",
  "early",
  "family",
  "apply",
  "reply",
  "supply",
  "daily",
  "holy",
  "rely",
  "ugly",
  "ally",
  "bully",
  "rally",
  "tally",
  "belly",
  "jelly",
  "folly",
  "jolly",
  "lily",
  "fly",
  "july",
  "sly",
  "ply",
  "italy",
  "anomaly"
]);
var EXCEPTIONS_ER = /* @__PURE__ */ new Set([
  "user",
  "server",
  "number",
  "member",
  "remember",
  "other",
  "never",
  "ever",
  "over",
  "under",
  "after",
  "water",
  "order",
  "power",
  "paper",
  "later",
  "letter",
  "center",
  "computer",
  "however",
  "together",
  "matter",
  "layer",
  "player",
  "river",
  "silver",
  "finger",
  "wonder",
  "cluster",
  "trigger",
  "docker",
  "buffer",
  "folder",
  "header",
  "footer",
  "render",
  "handler",
  "parser",
  "router",
  "worker",
  "builder",
  "loader",
  "adapter",
  "wrapper",
  "container",
  "parameter",
  "character",
  "manager",
  "provider",
  "consumer",
  "producer",
  "observer",
  "resolver",
  "scheduler",
  "dispatcher",
  "controller",
  "middleware",
  "whatever",
  "whenever",
  "wherever",
  "either",
  "neither",
  "rather",
  "whether",
  "another",
  "enter",
  "offer",
  "differ",
  "suffer",
  "prefer",
  "refer",
  "transfer",
  "master",
  "monster",
  "register",
  "consider",
  "discover",
  "deliver",
  "cover",
  "recover",
  "flutter",
  "twitter",
  "inner",
  "outer",
  "upper",
  "lower",
  "proper",
  "super",
  "fiber",
  "timber",
  "cider",
  "spider",
  "cyber"
]);
var EXCEPTIONS_EST = /* @__PURE__ */ new Set([
  "test",
  "best",
  "rest",
  "request",
  "nest",
  "west",
  "quest",
  "jest",
  "fest",
  "zest",
  "chest",
  "guest",
  "forest",
  "interest",
  "suggest",
  "manifest",
  "contest",
  "protest",
  "harvest",
  "invest",
  "digest",
  "modest",
  "honest",
  "earnest",
  "vitest",
  "latest"
]);
var EXCEPTIONS_NESS = /* @__PURE__ */ new Set([
  "business",
  "less",
  "ness"
]);
var KEEP_DOUBLED = /* @__PURE__ */ new Set(["ll", "ss", "ff", "zz"]);
var POST_STEM_MAP = {
  cach: "cache",
  rout: "route",
  styl: "style",
  revalidat: "revalidate",
  configur: "configure",
  configura: "configure",
  optimiz: "optimize",
  optimiza: "optimize",
  authentica: "authenticate",
  schedul: "schedule",
  initializ: "initialize",
  serializ: "serialize",
  deserializ: "deserialize",
  customiz: "customize",
  synchroniz: "synchronize"
};
function undouble(stem) {
  if (stem.length < 3) return stem;
  const last = stem[stem.length - 1];
  const prev = stem[stem.length - 2];
  if (last === prev && /[bcdfghjklmnpqrstvwxyz]/.test(last)) {
    const pair = `${prev}${last}`;
    if (!KEEP_DOUBLED.has(pair)) {
      return stem.slice(0, -1);
    }
  }
  return stem;
}
var MIN_STEM = 3;
function stemToken(word) {
  if (word.length < 4) return word;
  let stem = null;
  if (word.endsWith("tion") && word.length >= MIN_STEM + 4) {
    if (!EXCEPTIONS_TION.has(word)) stem = word.slice(0, -4);
  }
  if (stem === null && word.endsWith("ment") && word.length >= MIN_STEM + 4) {
    if (!EXCEPTIONS_MENT.has(word)) stem = word.slice(0, -4);
  }
  if (stem === null && word.endsWith("ness") && word.length >= MIN_STEM + 4) {
    if (!EXCEPTIONS_NESS.has(word)) stem = word.slice(0, -4);
  }
  if (stem === null && word.endsWith("ing") && word.length >= MIN_STEM + 3) {
    if (!EXCEPTIONS_ING.has(word)) stem = undouble(word.slice(0, -3));
  }
  if (stem === null && word.endsWith("est") && word.length >= MIN_STEM + 3) {
    if (!EXCEPTIONS_EST.has(word)) stem = undouble(word.slice(0, -3));
  }
  if (stem === null && word.endsWith("ed") && word.length >= MIN_STEM + 2) {
    if (!EXCEPTIONS_ED.has(word)) stem = undouble(word.slice(0, -2));
  }
  if (stem === null && word.endsWith("ly") && word.length >= 4 + 2) {
    if (!EXCEPTIONS_LY.has(word)) stem = word.slice(0, -2);
  }
  if (stem === null && word.endsWith("er") && word.length >= 4 + 2) {
    if (!EXCEPTIONS_ER.has(word)) stem = undouble(word.slice(0, -2));
  }
  if (stem === null) return word;
  return POST_STEM_MAP[stem] ?? stem;
}
function stemText(text) {
  return text.replace(/[a-z]+/g, (match) => stemToken(match));
}
export {
  stemText,
  stemToken
};
