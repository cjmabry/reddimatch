var webdriverio = require('webdriverio');
var options = {
    desiredCapabilities: {
        browserName: 'chrome',
        platformName: 'mac'
    }
};

// var options = {
//     waitforTimeout: 5000,
//     desiredCapabilities: {
//     	platformName: 'android',                        // operating system
//       browserName: 'chrome',
//       deviceName:'emulator-5554'
//     },
//     host: 'localhost',                                  // localhost
//     port: 4723                                          // port for appium
// };

// var options = {
//     waitforTimeout: 5000,
//     desiredCapabilities: {
//     	platformName: 'ios',
//       platformVersion: '8.4',
//       browserName: 'safari',
//       deviceName: 'iPhone 5',
//       nativeWebTap: true
//     },
//     host: 'localhost',                                  // localhost
//     port: 4723                                          // port for appium
// };

var url = './screenshots/' + options.desiredCapabilities.platformName + '/' + options.desiredCapabilities.browserName;

webdriverio
    .remote(options)
    .init()
    .url('http://localhost:8000')
    .saveScreenshot(url + '/home.png')
    .click('a.btn.btn-primary')
    .pause(2000)
    .setValue('input#user_login','cjmabry')
    .setValue('input#passwd_login','cjm444')
    .submitForm('form#login-form')
    .pause(3000)
    .click('input.allow')
    .pause(3000)
    .saveScreenshot(url + '/register.png')
    .setValue('input#username','cjmabry')
    .setValue('input#email','cjmab28@gmail.com')
    .setValue('textarea#bio','This is my bio!')
    .click('label.next-button')
    .pause(2000)
    .saveScreenshot(url + '/date_match.png')
    .click('div.icon')
    .pause(3000)
    .saveScreenshot(url + '/results.png')
    .scroll('.matches :nth-Child(1) .check')
    .click('.matches :nth-Child(1) .check')
    .pause(1000)
    .scroll('.matches :nth-Child(2) .cross')
    .click('.matches :nth-Child(2) .cross')
    .pause(3000)
    .saveScreenshot(url + '/accept_match.png')
    .click('a.btn-primary')
    .pause(5000)
    .saveScreenshot(url + '/chat.png')
    .end();
