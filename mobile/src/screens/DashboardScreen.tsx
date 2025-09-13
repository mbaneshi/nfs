import React from 'react';
import {View, StyleSheet, ScrollView} from 'react-native';
import {
  Card,
  Title,
  Paragraph,
  Button,
  Surface,
  Text,
} from 'react-native-paper';
import {useNavigation} from '@react-navigation/native';

export const DashboardScreen: React.FC = () => {
  const navigation = useNavigation();

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Title style={styles.title}>Dashboard</Title>
        <Paragraph style={styles.subtitle}>
          Welcome to NSF Multi-Platform AI Automation
        </Paragraph>
      </View>

      <View style={styles.cardsContainer}>
        <Card style={styles.card}>
          <Card.Content>
            <Title>API Status</Title>
            <Paragraph>Backend services are running</Paragraph>
            <Surface style={styles.statusIndicator}>
              <Text style={styles.statusText}>✓ Healthy</Text>
            </Surface>
          </Card.Content>
        </Card>

        <Card style={styles.card}>
          <Card.Content>
            <Title>Automation Platform</Title>
            <Paragraph>n8n workflows are active</Paragraph>
            <Surface style={styles.statusIndicator}>
              <Text style={styles.statusText}>✓ Active</Text>
            </Surface>
          </Card.Content>
        </Card>

        <Card style={styles.card}>
          <Card.Content>
            <Title>Database</Title>
            <Paragraph>Supabase connection established</Paragraph>
            <Surface style={styles.statusIndicator}>
              <Text style={styles.statusText}>✓ Connected</Text>
            </Surface>
          </Card.Content>
        </Card>
      </View>

      <View style={styles.actionsContainer}>
        <Button
          mode="contained"
          onPress={() => navigation.navigate('Automation' as never)}
          style={styles.button}>
          Open Automation
        </Button>
        <Button
          mode="outlined"
          onPress={() => {}}
          style={styles.button}>
          View Analytics
        </Button>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {
    padding: 20,
    backgroundColor: '#ffffff',
    marginBottom: 10,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 5,
  },
  subtitle: {
    fontSize: 16,
    color: '#666666',
  },
  cardsContainer: {
    padding: 20,
  },
  card: {
    marginBottom: 15,
    elevation: 2,
  },
  statusIndicator: {
    backgroundColor: '#4CAF50',
    paddingHorizontal: 10,
    paddingVertical: 5,
    borderRadius: 15,
    alignSelf: 'flex-start',
    marginTop: 10,
  },
  statusText: {
    color: '#ffffff',
    fontWeight: 'bold',
    fontSize: 12,
  },
  actionsContainer: {
    padding: 20,
  },
  button: {
    marginBottom: 10,
  },
});
