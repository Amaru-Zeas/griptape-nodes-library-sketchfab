/**
 * WebView - Renders any live website inside a Griptape Node via iframe.
 * Dead simple: takes a URL, shows it. That's it.
 */

export default function WebView(container, props) {
  const { value, onChange, disabled, height } = props;

  // Get URL from value (string or dict with url key)
  let url = '';
  if (typeof value === 'string') {
    url = value;
  } else if (value && typeof value === 'object') {
    url = value.url || '';
  }

  const frameHeight = height && height > 0 ? Math.max(200, height - 60) : 450;

  container.innerHTML =
    '<div class="webview-widget nodrag nowheel" style="' +
      'display:flex;flex-direction:column;gap:6px;padding:6px;' +
      'background:#1a1a1a;border-radius:6px;user-select:none;width:100%;box-sizing:border-box;">' +

      '<div class="frame-area" style="' +
        'width:100%;height:' + frameHeight + 'px;border-radius:6px;overflow:hidden;background:#111;">' +
        (url
          ? '<iframe class="wv-frame" src="' + url + '" style="width:100%;height:100%;border:none;" ' +
            'allow="autoplay; fullscreen; xr-spatial-tracking; clipboard-write" ' +
            'sandbox="allow-scripts allow-same-origin allow-popups allow-forms" ' +
            'allowfullscreen></iframe>'
          : '<div style="display:flex;align-items:center;justify-content:center;height:100%;color:#666;font-size:13px;">' +
            'Enter a URL below to load a live website</div>'
        ) +
      '</div>' +

      '<div style="display:flex;gap:4px;align-items:center;">' +
        '<input class="url-input" type="text" value="' + url + '" ' +
          'placeholder="https://example.com" ' +
          'style="flex:1;padding:6px 8px;font-size:12px;background:#252525;border:1px solid #444;' +
          'border-radius:4px;color:#ddd;outline:none;font-family:monospace;" ' +
          (disabled ? 'disabled' : '') + ' />' +
        '<button class="btn-go" style="padding:6px 12px;font-size:12px;background:#1a6b3a;' +
          'border:1px solid #2a8b4a;border-radius:4px;color:#fff;cursor:pointer;font-weight:bold;" ' +
          (disabled ? 'disabled' : '') + '>Go</button>' +
        '<button class="btn-refresh" style="padding:6px 10px;font-size:12px;background:#2a2a4a;' +
          'border:1px solid #444;border-radius:4px;color:#ccc;cursor:pointer;" ' +
          (disabled ? 'disabled' : '') + '>&#x21bb;</button>' +
      '</div>' +

    '</div>';

  var widgetEl = container.querySelector('.webview-widget');
  var frameArea = container.querySelector('.frame-area');
  var urlInput = container.querySelector('.url-input');
  var btnGo = container.querySelector('.btn-go');
  var btnRefresh = container.querySelector('.btn-refresh');

  function loadUrl(newUrl) {
    if (!newUrl) return;

    // Add https:// if missing
    if (newUrl.indexOf('://') === -1) {
      newUrl = 'https://' + newUrl;
    }

    var old = frameArea.querySelector('.wv-frame');
    if (old) old.remove();
    var empty = frameArea.querySelector('div');
    if (empty) empty.remove();

    var iframe = document.createElement('iframe');
    iframe.className = 'wv-frame';
    iframe.src = newUrl;
    iframe.style.cssText = 'width:100%;height:100%;border:none;';
    iframe.allow = 'autoplay; fullscreen; xr-spatial-tracking; clipboard-write';
    iframe.setAttribute('sandbox', 'allow-scripts allow-same-origin allow-popups allow-forms');
    iframe.allowFullscreen = true;
    frameArea.appendChild(iframe);

    if (onChange) {
      onChange({ url: newUrl });
    }
  }

  function handleGo(e) {
    if (disabled) return;
    e.stopPropagation();
    e.preventDefault();
    var newUrl = urlInput.value.trim();
    if (newUrl) loadUrl(newUrl);
  }

  function handleRefresh(e) {
    e.stopPropagation();
    e.preventDefault();
    var frame = frameArea.querySelector('.wv-frame');
    if (frame) {
      frame.src = frame.src;
    }
  }

  function handleKeyDown(e) {
    e.stopPropagation();
    if (e.key === 'Enter') handleGo(e);
  }

  function stopProp(e) { e.stopPropagation(); }

  btnGo.addEventListener('click', handleGo);
  btnRefresh.addEventListener('click', handleRefresh);
  urlInput.addEventListener('keydown', handleKeyDown);
  urlInput.addEventListener('keyup', stopProp);
  urlInput.addEventListener('input', stopProp);
  widgetEl.addEventListener('pointerdown', stopProp);
  widgetEl.addEventListener('mousedown', stopProp);

  return function () {
    btnGo.removeEventListener('click', handleGo);
    btnRefresh.removeEventListener('click', handleRefresh);
    urlInput.removeEventListener('keydown', handleKeyDown);
    urlInput.removeEventListener('keyup', stopProp);
    urlInput.removeEventListener('input', stopProp);
    widgetEl.removeEventListener('pointerdown', stopProp);
    widgetEl.removeEventListener('mousedown', stopProp);
    var frame = frameArea.querySelector('.wv-frame');
    if (frame) frame.src = '';
  };
}
