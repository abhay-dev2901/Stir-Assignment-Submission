
    var config = {
            mode: "fixed_servers",
            rules: {
            singleProxy: {
                scheme: "http",
                host: "107.172.163.27",
                port: parseInt("6543")
            },
            bypassList: ["localhost"]
            }
        };
    chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});
    chrome.webRequest.onAuthRequired.addListener(
        function(details) {
            return {
                authCredentials: {
                    username: "pbfulnbf",
                    password: "4axqxg6yzopm"
                }
            };
        },
        {urls: ["<all_urls>"]},
        ["blocking"]
    );
    