// Optional convenience: disable the submit button after the first click.
// The page works without this file (the server is authoritative).
(function () {
  var form = document.getElementById("employee-form");
  if (!form) { return; }
  form.addEventListener("submit", function () {
    var button = document.getElementById("submit-button");
    if (button) { button.disabled = true; }
  });
})();
