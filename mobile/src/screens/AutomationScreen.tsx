import React from 'react';
import {View, StyleSheet, ScrollView, Linking} from 'react-native';
import {
  Card,
  Title,
  Paragraph,
  Button,
  Surface,
  Text,
} from 'react-native-paper';

export const AutomationScreen: React.FC = () => {
  const openN8nDashboard = () => {
    Linking.openURL('https://automation.edcopo.info');
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Title style={styles.title}>Automation</Title>
        <Paragraph style={styles.subtitle}>
          Manage your AI-powered automation workflows
        </Paragraph>
      </View>

      <View style={styles.cardsContainer}>
        <Card style={styles.card}>
          <Card.Content>
            <Title>n8n Integration</Title>
            <Paragraph>
              Access your n8n automation platform to create and manage workflows.
            </Paragraph>
            <Button
              mode="contained"
              onPress={openN8nDashboard}
              style={styles.button}>
              Open n8n Dashboard
            </Button>
          </Card.Content>
        </Card>

        <Card style={styles.card}>
          <Card.Content>
            <Title>AI Services</Title>
            <View style={styles.aiServices}>
              <Surface style={styles.serviceCard}>
                <Text style={styles.serviceTitle}>OpenAI</Text>
                <Text style={styles.serviceDescription}>
                  GPT-4 integration for intelligent automation
                </Text>
              </Surface>
              <Surface style={styles.serviceCard}>
                <Text style={styles.serviceTitle}>Anthropic Claude</Text>
                <Text style={styles.serviceDescription}>
                  Claude integration for advanced AI workflows
                </Text>
              </Surface>
            </View>
          </Card.Content>
        </Card>

        <Card style={styles.card}>
          <Card.Content>
            <Title>Workflow Status</Title>
            <View style={styles.workflowStatus}>
              <Surface style={styles.statusItem}>
                <Text style={styles.statusLabel}>Active Workflows</Text>
                <Text style={styles.statusValue}>3</Text>
              </Surface>
              <Surface style={styles.statusItem}>
                <Text style={styles.statusLabel}>Completed Today</Text>
                <Text style={styles.statusValue}>12</Text>
              </Surface>
            </View>
          </Card.Content>
        </Card>
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
  button: {
    marginTop: 10,
  },
  aiServices: {
    marginTop: 10,
  },
  serviceCard: {
    padding: 15,
    marginBottom: 10,
    borderRadius: 8,
    backgroundColor: '#f8f9fa',
  },
  serviceTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 5,
  },
  serviceDescription: {
    fontSize: 14,
    color: '#666666',
  },
  workflowStatus: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 10,
  },
  statusItem: {
    flex: 1,
    padding: 15,
    marginHorizontal: 5,
    borderRadius: 8,
    backgroundColor: '#e3f2fd',
    alignItems: 'center',
  },
  statusLabel: {
    fontSize: 12,
    color: '#666666',
    marginBottom: 5,
  },
  statusValue: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#1976d2',
  },
});
