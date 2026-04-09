// Cloudflare Worker - IP检测服务
// 部署到 Cloudflare Workers（免费），获得一个URL如 https://ip-check.你的域名.workers.dev

export default {
  async fetch(request) {
    // 获取访问者IP
    const clientIP = request.headers.get('CF-Connecting-IP') || 'unknown';
    
    // 调用ip-api检测质量
    let quality = {};
    try {
      const resp = await fetch(`http://ip-api.com/json/${clientIP}?fields=query,country,city,isp,org,proxy,hosting`);
      quality = await resp.json();
    } catch (e) {
      quality = { query: clientIP, error: 'API调用失败' };
    }
    
    // 判断是否干净
    const isClean = quality.proxy === false && quality.hosting === false;
    quality.status = isClean ? '✅ 干净住宅IP' : '❌ 代理/数据中心IP';
    
    // 返回结果
    return new Response(JSON.stringify(quality, null, 2), {
      headers: { 
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
      }
    });
  }
};
