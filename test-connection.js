// simple test to verify backend connection
const axios = require('axios');

const API_BASE_URL = 'https://agentic-doctor-appointment-system.onrender.com';

async function testConnection() {
  console.log(' Testing backend connection...');
  console.log(`Backend URL: ${API_BASE_URL}`);
  
  try {
    // test health endpoint
    console.log('\n1. Testing health endpoint...');
    const healthResponse = await axios.get(`${API_BASE_URL}/health`);
    console.log(' Health check passed:', healthResponse.data.status);
    
    // test agents status
    console.log('\n2. Testing agents status...');
    const agentsResponse = await axios.get(`${API_BASE_URL}/agents/status`);
    console.log(' Agents active:', agentsResponse.data.agents.length);
    
    // test chat api
    console.log('\n3. Testing chat API...');
    const chatResponse = await axios.post(`${API_BASE_URL}/execute`, {
      id_number: 12345678,
      messages: [{ role: 'user', content: 'Hello, test message' }],
      intent: 'info_request'
    });
    console.log(' Chat API working:', chatResponse.data.messages.length, 'messages');
    console.log(' AI Response:', chatResponse.data.messages[chatResponse.data.messages.length - 1].content.substring(0, 100) + '...');
    
    console.log('\n All tests passed! Backend is ready for frontend connection.');
    
  } catch (error) {
    console.error(' Connection test failed:', error.message);
    if (error.response) {
      console.error('Response status:', error.response.status);
      console.error('Response data:', error.response.data);
    }
  }
}

testConnection();