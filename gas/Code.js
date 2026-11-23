// 141회 공정표 동기화 — 기록은 내 드라이브의 JSON 파일 하나에 저장
const FILE = '141회_공정표_동기화.json';
function secret_() { return PropertiesService.getScriptProperties().getProperty('KEY'); }
function file_() {
  const it = DriveApp.getFilesByName(FILE);
  return it.hasNext() ? it.next() : DriveApp.createFile(FILE, '{"c":{},"i":{},"w":{},"n":{}}', 'application/json');
}
function out_(o) { return ContentService.createTextOutput(JSON.stringify(o)).setMimeType(ContentService.MimeType.JSON); }
function merge_(a, b) {
  const o = {};
  ['c', 'i', 'w', 'n'].forEach(cat => {
    o[cat] = Object.assign({}, (a && a[cat]) || {});
    Object.entries((b && b[cat]) || {}).forEach(([k, v]) => { if (!o[cat][k] || o[cat][k][1] < v[1]) o[cat][k] = v; });
  });
  return o;
}
function doGet(e) {
  if (!e.parameter.k || e.parameter.k !== secret_()) return out_({ err: 'key' });
  return out_({ s: JSON.parse(file_().getBlob().getDataAsString()) });
}
function doPost(e) {
  const b = JSON.parse(e.postData.contents);
  if (!b.k || b.k !== secret_()) return out_({ err: 'key' });
  const lock = LockService.getScriptLock(); lock.waitLock(10000);
  try {
    const f = file_();
    const m = merge_(JSON.parse(f.getBlob().getDataAsString()), b.s);
    f.setContent(JSON.stringify(m));
    return out_({ s: m });
  } finally { lock.releaseLock(); }
}
// 처음 한 번: 편집기에서 setup 실행 → 동기화 코드 생성
function setup() {
  let k = secret_();
  if (!k) { k = Utilities.getUuid().replace(/-/g, '').slice(0, 16); PropertiesService.getScriptProperties().setProperty('KEY', k); }
  file_();
  Logger.log('동기화 코드: ' + k);
  return k;
}
