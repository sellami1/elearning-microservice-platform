const mongoose = require('mongoose');

// No real DB connection needed as we will mock the models
beforeAll(async () => {
  console.log('Test setup: Mocking database operations.');
});

afterAll(async () => {
  // Nothing to cleanup
});

afterEach(async () => {
  jest.clearAllMocks();
});
