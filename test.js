return(function(platform, screenWidth, screenAvailWidth, windowOuterWidth, windowInnerWidth,
        screenHeight, screenAvailHeight, windowOuterHeight, windowInnerHeight,screenColorDepth,
         screenPixelDepth, navigatorUserAgent,navigatorCookieEnabled, navigatorDeviceMemory) {


        console.log("Executing device configuration");

        /* Width properties */
        Object.defineProperty(window.screen, 'width', {value: screenWidth});
        Object.defineProperty(window.screen, 'availWidth', {value: screenAvailWidth});

        Object.defineProperty(window, 'outerWidth', {value: windowOuterWidth});
        Object.defineProperty(window, 'innerWidth', {value: windowInnerWidth});

        /* Height properties */
        Object.defineProperty(window.screen, 'height', {value: screenHeight});
        Object.defineProperty(window.screen, 'availHeight', {value: screenAvailHeight});

        Object.defineProperty(window, 'outerHeight', {value: windowOuterHeight});
        Object.defineProperty(window, 'innerHeight', {value: windowInnerHeight});

        /* Other windows.screen properties */
        Object.defineProperty(window.screen, 'colorDepth', {value: screenColorDepth});
        Object.defineProperty(window.screen, 'pixelDepth', {value: screenPixelDepth});

        /* Other navigator properties */
        Object.defineProperty(window.navigator, 'platform', {value: platform});
        Object.defineProperty(window.navigator, 'cookieEnabled', {value: navigatorCookieEnabled});
        Object.defineProperty(window.navigator, 'deviceMemory', {value: navigatorDeviceMemory});

        /* Spoofing navigator.userAgentData object */
        var userAgentDataClone = Object;
        Object.assign(userAgentDataClone, JSON.parse(JSON.stringify(window.navigator.userAgentData)));
        userAgentDataClone.platform = platform;

        Object.defineProperty( window.navigator, 'userAgentData', {
            value: userAgentDataClone,
            writable: true,
            enumerable: true,
            configurable: true,
        });
        console.log("Executed device configuration successfully");
        return "Done";
})("%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s")