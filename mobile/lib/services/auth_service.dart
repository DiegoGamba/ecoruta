import 'package:amplify_auth_cognito/amplify_auth_cognito.dart';
import 'package:amplify_flutter/amplify_flutter.dart';

/// Autenticación contra Cognito. El token se guarda y refresca en el llavero
/// seguro del dispositivo (Keychain / Keystore) que administra Amplify: la app
/// nunca persiste credenciales por su cuenta.
class AuthService {
  Future<void> configure(String userPoolId, String clientId, String region) async {
    if (Amplify.isConfigured) return;
    await Amplify.addPlugin(AmplifyAuthCognito());
    await Amplify.configure('''
    {
      "auth": {
        "plugins": {
          "awsCognitoAuthPlugin": {
            "CognitoUserPool": {
              "Default": {
                "PoolId": "$userPoolId",
                "AppClientId": "$clientId",
                "Region": "$region"
              }
            }
          }
        }
      }
    }
    ''');
  }

  Future<bool> isSignedIn() async =>
      (await Amplify.Auth.fetchAuthSession()).isSignedIn;

  Future<void> signIn(String email, String password) async {
    await Amplify.Auth.signIn(username: email, password: password);
  }

  Future<void> signUp(String email, String password) async {
    await Amplify.Auth.signUp(
      username: email,
      password: password,
      options: SignUpOptions(userAttributes: {AuthUserAttributeKey.email: email}),
    );
  }

  Future<void> confirm(String email, String code) async {
    await Amplify.Auth.confirmSignUp(username: email, confirmationCode: code);
  }

  Future<void> signOut() => Amplify.Auth.signOut();

  Future<String> accessToken() async {
    final session = await Amplify.Auth.fetchAuthSession(
      options: const FetchAuthSessionOptions(forceRefresh: false),
    ) as CognitoAuthSession;
    final token = session.userPoolTokensResult.value.accessToken.raw;
    if (token.isEmpty) throw StateError('sesión sin token válido');
    return token;
  }
}
