// Exists only so Chrome's install-prompt algorithm sees a registered fetch
// handler (see dashboard.py's registration comment for why). Deliberately
// does no caching: this page changes daily, and a cache-first worker would
// risk serving yesterday's regulatory data as if it were current. Every
// request falls straight through to the network.
self.addEventListener('fetch', () => {});
