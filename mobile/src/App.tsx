import React from 'react';
import {NavigationContainer} from '@react-navigation/native';
import {createStackNavigator} from '@react-navigation/stack';
import {Provider as PaperProvider} from 'react-native-paper';
import {StatusBar} from 'react-native';

import {DashboardScreen} from './src/screens/DashboardScreen';
import {AutomationScreen} from './src/screens/AutomationScreen';
import {theme} from './src/utils/theme';

const Stack = createStackNavigator();

const App: React.FC = () => {
  return (
    <PaperProvider theme={theme}>
      <NavigationContainer>
        <StatusBar barStyle="dark-content" backgroundColor="#ffffff" />
        <Stack.Navigator
          initialRouteName="Dashboard"
          screenOptions={{
            headerStyle: {
              backgroundColor: '#ffffff',
            },
            headerTintColor: '#000000',
            headerTitleStyle: {
              fontWeight: 'bold',
            },
          }}>
          <Stack.Screen
            name="Dashboard"
            component={DashboardScreen}
            options={{title: 'NSF AI Automation'}}
          />
          <Stack.Screen
            name="Automation"
            component={AutomationScreen}
            options={{title: 'Automation'}}
          />
        </Stack.Navigator>
      </NavigationContainer>
    </PaperProvider>
  );
};

export default App;
