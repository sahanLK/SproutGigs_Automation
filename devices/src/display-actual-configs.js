/* Display the actual configuration values */


/* Window */
$('#innerwidth').text(window.innerWidth);
$('#innerheight').text(window.innerHeight);
$('#outerwidth').text(window.outerWidth);
$('#outerheight').text(window.outerHeight);

/* Window.Navigator */
$('#useragent').text(window.navigator.userAgent);
$('#cookieenabled').text(window.navigator.cookieEnabled);
$('#appcodename').text(window.navigator.appCodeName);
$('#platform').text(window.navigator.platform);
$('#webdriver').text(window.navigator.webdriver);
$('#devicememory').text(window.navigator.deviceMemory);

/* Window.Screen */
$('#width').text(window.screen.width);
$('#height').text(window.screen.height);
$('#availwidth').text(window.screen.availWidth);
$('#availheight').text(window.screen.availHeight);
$('#colordepth').text(window.screen.colorDepth);
$('#pixeldepth').text(window.screen.pixelDepth);
console.log("Updated actual values successfully from Footer.txt");