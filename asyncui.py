import aiohttp, asyncio, async_timeout
import ui, objc_util

class AsyncUIView(ui.View):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.running = True
    #self._loop = asyncio.get_event_loop()
    self._loop = asyncio.get_event_loop_policy().new_event_loop()
    self._loop.set_debug(True)
    self._session = aiohttp.ClientSession(loop=self._loop)
    
  def will_close(self):
    self.running = False
    
  def start_loop(self):
    try:
      self._loop.run_until_complete(self._runner())
    finally:
      if not self._session.closed:
        self._session.close()
      self._loop.close()
    
  async def _runner(self):
    while self.running:
      await self._loop.create_task(asyncio.sleep(0.5))
    
  def call_soon(self, coro):
    asyncio.set_event_loop(self._loop)
    self._loop.call_soon_threadsafe(lambda: asyncio.ensure_future(coro))
      
  async def get(self, url):
    with async_timeout.timeout(10):
      async with self._session.get(url) as response:
        return await response.text()
  
if __name__ == '__main__':
  
  class DemoView(ui.View):
    def __init__(self, *args, **kwargs):
      super().__init__(*args, **kwargs)
      self.web1 = ui.WebView(flex='WH', frame=(0,0,self.width,self.height/2))
      self.add_subview(self.web1)
      self.web2 = ui.WebView(flex='WH', frame=(0,self.height/2,self.width,self.height/2))
      self.add_subview(self.web2)
      self.counter = 0
      self.btn = btn = ui.Button(flex='WH', frame=self.bounds, tint_color=(.77, .22, .03), action=self.do_fetch)
      self.add_subview(btn)
      self.update_interval = 0.5
    
    def update(self):
      self.counter += 1
      self.btn.title = f'#{self.counter} - Click me'
      
    def do_fetch(self, sender):
      loading = '<span style="font-size: xx-large;">Loading...</span>'
      
      self.web1.load_html(loading)
      aui.call_soon(self.load_page('http://python.org', self.web1))
      
      self.web2.load_html(loading)
      aui.call_soon(self.load_page('http://omz-software.com/pythonista/', self.web2))
      
    async def load_page(self, url, webview):
      html = await aui.get(url)
      webview.load_html(html)

    
  aui = AsyncUIView()
  aui.present('full_screen')
  
  aui.add_subview(DemoView(frame=aui.bounds))
  
  aui.start_loop()
