/**
 * SketchfabViewer - Embeds an interactive Sketchfab 3D model viewer inside a Griptape Node.
 * Uses a plain iframe with the Sketchfab embed URL for maximum compatibility.
 * Reference: https://sketchfab.com/developers/viewer
 */

export default function SketchfabViewer(container, props) {
  const { value, onChange, disabled, height } = props;

  // Parse the model UID from value (dict or string)
  let modelUid = '';
  if (value && typeof value === 'object') {
    modelUid = value.model_uid || '';
  } else if (typeof value === 'string') {
    modelUid = value;
  }
  modelUid = extractUid(modelUid);

  const viewerHeight = height && height > 0 ? Math.max(250, height - 80) : 400;

  // Build the embed URL
  const embedUrl = modelUid
    ? 'https://sketchfab.com/models/' + modelUid + '/embed?autostart=1&ui_theme=dark'
    : '';

  // Create the DOM
  container.innerHTML =
    '<div class="sketchfab-widget nodrag nowheel" style="' +
      'display:flex;flex-direction:column;gap:6px;padding:8px;' +
      'background:#1a1a1a;border-radius:6px;user-select:none;width:100%;box-sizing:border-box;">' +

      '<div class="viewer-area" style="' +
        'width:100%;height:' + viewerHeight + 'px;border-radius:6px;overflow:hidden;background:#111;position:relative;">' +
        (embedUrl
          ? '<iframe class="sf-iframe" src="' + embedUrl + '" style="width:100%;height:100%;border:none;" ' +
            'allow="autoplay; fullscreen; xr-spatial-tracking" ' +
            'allowfullscreen mozallowfullscreen="true" webkitallowfullscreen="true">' +
            '</iframe>'
          : '<div style="display:flex;align-items:center;justify-content:center;height:100%;color:#666;font-size:13px;">' +
            'Enter a Sketchfab model UID or URL below</div>'
        ) +
      '</div>' +

      '<div style="display:flex;gap:4px;align-items:center;">' +
        '<input class="uid-input" type="text" value="' + modelUid + '" ' +
          'placeholder="Paste Sketchfab model UID or URL..." ' +
          'style="flex:1;padding:6px 8px;font-size:12px;background:#252525;border:1px solid #444;' +
          'border-radius:4px;color:#ddd;outline:none;font-family:monospace;" ' +
          (disabled ? 'disabled' : '') + ' />' +
        '<button class="btn-load" style="padding:6px 12px;font-size:12px;background:#1a6b3a;' +
          'border:1px solid #2a8b4a;border-radius:4px;color:#fff;cursor:pointer;font-weight:bold;" ' +
          (disabled ? 'disabled' : '') + '>Load</button>' +
      '</div>' +

    '</div>';

  // DOM references
  var widgetEl = container.querySelector('.sketchfab-widget');
  var viewerArea = container.querySelector('.viewer-area');
  var uidInput = container.querySelector('.uid-input');
  var loadBtn = container.querySelector('.btn-load');

  // Load a model by UID
  function loadModel(uid) {
    if (!uid) return;

    // Remove old iframe
    var oldFrame = viewerArea.querySelector('.sf-iframe');
    if (oldFrame) oldFrame.remove();

    // Remove empty state
    var emptyDiv = viewerArea.querySelector('div');
    if (emptyDiv) emptyDiv.remove();

    // Create new iframe
    var iframe = document.createElement('iframe');
    iframe.className = 'sf-iframe';
    iframe.src = 'https://sketchfab.com/models/' + uid + '/embed?autostart=1&ui_theme=dark';
    iframe.style.cssText = 'width:100%;height:100%;border:none;';
    iframe.allow = 'autoplay; fullscreen; xr-spatial-tracking';
    iframe.allowFullscreen = true;
    iframe.setAttribute('mozallowfullscreen', 'true');
    iframe.setAttribute('webkitallowfullscreen', 'true');
    viewerArea.appendChild(iframe);

    // Push value back
    if (onChange) {
      onChange({ model_uid: uid });
    }
  }

  // Extract UID from Sketchfab URLs
  function extractUid(input) {
    if (!input) return '';
    input = input.trim();
    if (input.indexOf('sketchfab.com') !== -1) {
      var hexMatch = input.match(/[/-]([a-f0-9]{32})(?:[/?#]|$)/);
      if (hexMatch) return hexMatch[1];
      var pathMatch = input.match(/\/([a-zA-Z0-9]+)(?:[/?#]|$)/);
      if (pathMatch) return pathMatch[1];
    }
    return input;
  }

  // Event: Load button click
  function handleLoad(e) {
    if (disabled) return;
    e.stopPropagation();
    e.preventDefault();
    var raw = uidInput.value.trim();
    var uid = extractUid(raw);
    if (uid) {
      uidInput.value = uid;
      loadModel(uid);
    }
  }

  // Event: Enter key in input
  function handleKeyDown(e) {
    e.stopPropagation();
    if (e.key === 'Enter') {
      handleLoad(e);
    }
  }

  // Prevent node drag/interaction on widget
  function stopProp(e) {
    e.stopPropagation();
  }

  // Attach events
  loadBtn.addEventListener('click', handleLoad);
  uidInput.addEventListener('keydown', handleKeyDown);
  uidInput.addEventListener('keyup', stopProp);
  uidInput.addEventListener('input', stopProp);
  widgetEl.addEventListener('pointerdown', stopProp);
  widgetEl.addEventListener('mousedown', stopProp);

  // Cleanup
  return function () {
    loadBtn.removeEventListener('click', handleLoad);
    uidInput.removeEventListener('keydown', handleKeyDown);
    uidInput.removeEventListener('keyup', stopProp);
    uidInput.removeEventListener('input', stopProp);
    widgetEl.removeEventListener('pointerdown', stopProp);
    widgetEl.removeEventListener('mousedown', stopProp);
    var iframe = viewerArea.querySelector('.sf-iframe');
    if (iframe) iframe.src = '';
  };
}
