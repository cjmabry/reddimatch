var webdriverio = require('webdriverio');
var mac_chrome = {
    desiredCapabilities: {
        browserName: 'chrome',
        platformName: 'mac'
    }
};

var android_chrome = {
    waitforTimeout: 5000,
    desiredCapabilities: {
    	platformName: 'android',                        // operating system
      browserName: 'chrome',
      deviceName:'emulator-5554'
    },
    host: 'localhost',                                  // localhost
    port: 4723                                          // port for appium
};

var ios_safari = {
    waitforTimeout: 5000,
    desiredCapabilities: {
    	platformName: 'ios',
      platformVersion: '8.4',
      browserName: 'safari',
      deviceName: 'iPhone 5',
      nativeWebTap: true
    },
    host: 'localhost',                                  // localhost
    port: 4723                                          // port for appium
};

var options = ios_safari;

var url = './screenshots/' + options.desiredCapabilities.platformName + '/' + options.desiredCapabilities.browserName;

webdriverio
    .remote(options)
    .init()
    .url('http://localhost:8000')
    .pause(3000)
    .saveScreenshot(url + '/home.png')
    .click('a.btn.btn-primary')
    .pause(2000)
    .setValue('input#user_login','cjmabry')
    .setValue('input#passwd_login','cjm444')
    .submitForm('form#login-form')
    .pause(3000)
    .click('input.allow')
    .pause(6000)
    .saveScreenshot(url + '/register.png')
    .pause(1000)
    .setValue('input#username','cjmabry')
    .pause(1000)
    .setValue('input#email','cjmab28@gmail.com')
    .pause(1000)
    .setValue('textarea#bio','This is my bio!')
    .pause(2000)
    .pause(1000)
    .element('label.next-button').click()
    .pause(2000)
    .saveScreenshot(url + '/date_match.png')
    .scroll('div.icon')
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
    .scroll('a.btn-primary')
    .click('a.btn-primary')
    .pause(5000)
    .saveScreenshot(url + '/chat.png')
    .end();
