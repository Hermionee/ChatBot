import CognitoAuth from './apiGateway-js-sdk/lib/amazon-cognito-auth-js/src/CognitoAuth.js';
// import AWS from './apiGateway-js-sdk/aws-sdk-2.349.0.min.js';
function initCognitoSDK(){
	

    //  var data = { UserPoolId : 'us-east-1_T0q2XiW52',
    //     ClientId : '7kl1nlprddl6r83710uid9b9la'
    // };
    // var userPool = new cognito.CognitoUserPool(data);
    // var cognitoUser = userPool.getCurrentUser();

    // if (cognitoUser != null) {
    //     cognitoUser.getSession(function(err, session) {
    //         if (err) {
    //             alert(err);
    //             return;
    //         }
    //         console.log('session validity: ' + session.isValid());
    //     });
    // }


var authData = {
    ClientId : '7kl1nlprddl6r83710uid9b9la', // Your client id here
    AppWebDomain : 'manhanttenduo.auth.us-east-1.amazoncognito.com',
    TokenScopesArray : ['phone', 'email', 'profile','openid', 'aws.cognito.signin.user.admin'], // e.g.['phone', 'email', 'profile','openid', 'aws.cognito.signin.user.admin'],
    RedirectUriSignIn : 'https://s3.amazonaws.com/manhanttenduo/index.html',
    RedirectUriSignOut : 'https://s3.amazonaws.com/manhanttenduo/index.html',
    // IdentityProvider : '<TODO: add identity provider you want to specify>', // e.g. 'Facebook',
    UserPoolId : 'us-east-1_T0q2XiW52', // Your user pool id here
    // AdvancedSecurityDataCollectionFlag : 'true', // e.g. true
        // Storage: 'new CookieStorage()' // OPTIONAL e.g. new CookieStorage(), to use the specified storage provided
};
var auth = new AmazonCognitoIdentity.CognitoAuth(authData);
  auth.userhandler = {
    onSuccess: function(result) {
        alert("Sign in success");

    },
    onFailure: function(err) {
        alert("Error!");
    }
};
auth.useCodeGrantFlow();
return auth;
}


    //  var authenticationData = {
    //     Username : 'username',
    //     Password : 'password',
    // };
    // var authenticationDetails = new AmazonCognitoIdentity.AuthenticationDetails(authenticationData);
    // var poolData = { UserPoolId : 'us-east-1_T0q2XiW52',
    //     ClientId : '7kl1nlprddl6r83710uid9b9la'
    // };
    // var userPool = new AmazonCognitoIdentity.CognitoUserPool(poolData);
    // var userData = {
    //     Username : 'username',
    //     Pool : userPool
    // };
    // var cognitoUser = new AmazonCognitoIdentity.CognitoUser(userData);
    // cognitoUser.authenticateUser(authenticationDetails, {
    //     onSuccess: function (result) {
    //         var accessToken = result.getAccessToken().getJwtToken();
            
    //         /* Use the idToken for Logins Map when Federating User Pools with identity pools or when passing through an Authorization Header to an API Gateway Authorizer*/
    //         var idToken = result.idToken.jwtToken;
    //     },

    //     onFailure: function(err) {
    //         alert(err);
    //     },

    // });

