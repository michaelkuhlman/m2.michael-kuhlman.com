const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1920,height:960}});
await p.goto('file:///tmp/m2hero/hero.html');await p.waitForTimeout(800);await p.screenshot({path:'/tmp/m2hero/hero.png'});
await p.screenshot({path:'/tmp/m2hero/hero.jpg',type:'jpeg',quality:86});await b.close()})()
