/**
 * TestWidget - The absolute simplest widget possible.
 * If this doesn't render, widgets aren't working in the engine.
 */

export default function TestWidget(container, props) {
  const { value, onChange, disabled } = props;

  container.innerHTML =
    '<div class="nodrag nowheel" style="padding:20px;background:#1a3a1a;border-radius:8px;text-align:center;">' +
      '<div style="font-size:18px;color:#4f4;margin-bottom:8px;">WIDGETS ARE WORKING</div>' +
      '<div style="font-size:12px;color:#aaa;">Value: ' + JSON.stringify(value) + '</div>' +
    '</div>';

  return function () {};
}
