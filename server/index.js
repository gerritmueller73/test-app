const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const fs = require('fs-extra');
const path = require('path');
const { v4: uuidv4 } = require('uuid');

const app = express();
const PORT = process.env.PORT || 5000;
const JWT_SECRET = process.env.JWT_SECRET || 'nutrition_coach_secret_key_2024';

// Middleware
app.use(cors());
app.use(bodyParser.json());
app.use(express.static(path.join(__dirname, '../client/build')));

// Data storage paths
const DATA_DIR = path.join(__dirname, 'data');
const USERS_FILE = path.join(DATA_DIR, 'users.json');
const MEALS_FILE = path.join(DATA_DIR, 'meals.json');
const NUTRITION_LOGS_FILE = path.join(DATA_DIR, 'nutrition_logs.json');
const FOOD_DATABASE_FILE = path.join(DATA_DIR, 'food_database.json');

// Ensure data directory and files exist
async function initializeData() {
  await fs.ensureDir(DATA_DIR);
  
  if (!await fs.pathExists(USERS_FILE)) {
    await fs.writeJson(USERS_FILE, []);
  }
  
  if (!await fs.pathExists(MEALS_FILE)) {
    await fs.writeJson(MEALS_FILE, []);
  }
  
  if (!await fs.pathExists(NUTRITION_LOGS_FILE)) {
    await fs.writeJson(NUTRITION_LOGS_FILE, []);
  }
  
  if (!await fs.pathExists(FOOD_DATABASE_FILE)) {
    await fs.writeJson(FOOD_DATABASE_FILE, [
      {
        id: '1',
        name: 'Chicken Breast',
        calories: 165,
        protein: 31,
        carbs: 0,
        fat: 3.6,
        fiber: 0,
        servingSize: '100g'
      },
      {
        id: '2',
        name: 'Brown Rice',
        calories: 111,
        protein: 2.6,
        carbs: 23,
        fat: 0.9,
        fiber: 1.8,
        servingSize: '100g'
      },
      {
        id: '3',
        name: 'Broccoli',
        calories: 34,
        protein: 2.8,
        carbs: 7,
        fat: 0.4,
        fiber: 2.6,
        servingSize: '100g'
      },
      {
        id: '4',
        name: 'Salmon',
        calories: 208,
        protein: 20,
        carbs: 0,
        fat: 12,
        fiber: 0,
        servingSize: '100g'
      },
      {
        id: '5',
        name: 'Sweet Potato',
        calories: 86,
        protein: 1.6,
        carbs: 20,
        fat: 0.1,
        fiber: 3,
        servingSize: '100g'
      }
    ]);
  }
}

// Authentication middleware
const authenticateToken = (req, res, next) => {
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1];

  if (!token) {
    return res.status(401).json({ message: 'Access token required' });
  }

  jwt.verify(token, JWT_SECRET, (err, user) => {
    if (err) {
      return res.status(403).json({ message: 'Invalid token' });
    }
    req.user = user;
    next();
  });
};

// Helper functions
async function readJsonFile(filePath) {
  try {
    return await fs.readJson(filePath);
  } catch (error) {
    return [];
  }
}

async function writeJsonFile(filePath, data) {
  await fs.writeJson(filePath, data, { spaces: 2 });
}

// Authentication routes
app.post('/api/auth/register', async (req, res) => {
  try {
    const { email, password, firstName, lastName, role = 'client' } = req.body;
    
    const users = await readJsonFile(USERS_FILE);
    
    if (users.find(user => user.email === email)) {
      return res.status(400).json({ message: 'User already exists' });
    }
    
    const hashedPassword = await bcrypt.hash(password, 10);
    const newUser = {
      id: uuidv4(),
      email,
      password: hashedPassword,
      firstName,
      lastName,
      role,
      profile: {
        age: null,
        gender: null,
        height: null,
        weight: null,
        activityLevel: null,
        goals: [],
        dietaryRestrictions: []
      },
      createdAt: new Date().toISOString()
    };
    
    users.push(newUser);
    await writeJsonFile(USERS_FILE, users);
    
    const token = jwt.sign(
      { userId: newUser.id, email: newUser.email, role: newUser.role },
      JWT_SECRET,
      { expiresIn: '7d' }
    );
    
    res.status(201).json({
      token,
      user: {
        id: newUser.id,
        email: newUser.email,
        firstName: newUser.firstName,
        lastName: newUser.lastName,
        role: newUser.role,
        profile: newUser.profile
      }
    });
  } catch (error) {
    res.status(500).json({ message: 'Server error', error: error.message });
  }
});

app.post('/api/auth/login', async (req, res) => {
  try {
    const { email, password } = req.body;
    
    const users = await readJsonFile(USERS_FILE);
    const user = users.find(u => u.email === email);
    
    if (!user) {
      return res.status(400).json({ message: 'Invalid credentials' });
    }
    
    const isValidPassword = await bcrypt.compare(password, user.password);
    if (!isValidPassword) {
      return res.status(400).json({ message: 'Invalid credentials' });
    }
    
    const token = jwt.sign(
      { userId: user.id, email: user.email, role: user.role },
      JWT_SECRET,
      { expiresIn: '7d' }
    );
    
    res.json({
      token,
      user: {
        id: user.id,
        email: user.email,
        firstName: user.firstName,
        lastName: user.lastName,
        role: user.role,
        profile: user.profile
      }
    });
  } catch (error) {
    res.status(500).json({ message: 'Server error', error: error.message });
  }
});

// User profile routes
app.get('/api/user/profile', authenticateToken, async (req, res) => {
  try {
    const users = await readJsonFile(USERS_FILE);
    const user = users.find(u => u.id === req.user.userId);
    
    if (!user) {
      return res.status(404).json({ message: 'User not found' });
    }
    
    res.json({
      id: user.id,
      email: user.email,
      firstName: user.firstName,
      lastName: user.lastName,
      role: user.role,
      profile: user.profile
    });
  } catch (error) {
    res.status(500).json({ message: 'Server error', error: error.message });
  }
});

app.put('/api/user/profile', authenticateToken, async (req, res) => {
  try {
    const users = await readJsonFile(USERS_FILE);
    const userIndex = users.findIndex(u => u.id === req.user.userId);
    
    if (userIndex === -1) {
      return res.status(404).json({ message: 'User not found' });
    }
    
    users[userIndex].profile = { ...users[userIndex].profile, ...req.body };
    await writeJsonFile(USERS_FILE, users);
    
    res.json({
      id: users[userIndex].id,
      email: users[userIndex].email,
      firstName: users[userIndex].firstName,
      lastName: users[userIndex].lastName,
      role: users[userIndex].role,
      profile: users[userIndex].profile
    });
  } catch (error) {
    res.status(500).json({ message: 'Server error', error: error.message });
  }
});

// Food database routes
app.get('/api/foods', authenticateToken, async (req, res) => {
  try {
    const foods = await readJsonFile(FOOD_DATABASE_FILE);
    const { search } = req.query;
    
    if (search) {
      const filteredFoods = foods.filter(food => 
        food.name.toLowerCase().includes(search.toLowerCase())
      );
      return res.json(filteredFoods);
    }
    
    res.json(foods);
  } catch (error) {
    res.status(500).json({ message: 'Server error', error: error.message });
  }
});

// Nutrition log routes
app.get('/api/nutrition-logs', authenticateToken, async (req, res) => {
  try {
    const logs = await readJsonFile(NUTRITION_LOGS_FILE);
    const userLogs = logs.filter(log => log.userId === req.user.userId);
    
    const { date } = req.query;
    if (date) {
      const dateStr = new Date(date).toISOString().split('T')[0];
      const dateLogs = userLogs.filter(log => log.date === dateStr);
      return res.json(dateLogs);
    }
    
    res.json(userLogs);
  } catch (error) {
    res.status(500).json({ message: 'Server error', error: error.message });
  }
});

app.post('/api/nutrition-logs', authenticateToken, async (req, res) => {
  try {
    const { foodId, quantity, mealType, date } = req.body;
    
    const foods = await readJsonFile(FOOD_DATABASE_FILE);
    const food = foods.find(f => f.id === foodId);
    
    if (!food) {
      return res.status(404).json({ message: 'Food not found' });
    }
    
    const logs = await readJsonFile(NUTRITION_LOGS_FILE);
    const newLog = {
      id: uuidv4(),
      userId: req.user.userId,
      foodId,
      foodName: food.name,
      quantity,
      mealType,
      date: new Date(date).toISOString().split('T')[0],
      calories: (food.calories * quantity) / 100,
      protein: (food.protein * quantity) / 100,
      carbs: (food.carbs * quantity) / 100,
      fat: (food.fat * quantity) / 100,
      fiber: (food.fiber * quantity) / 100,
      createdAt: new Date().toISOString()
    };
    
    logs.push(newLog);
    await writeJsonFile(NUTRITION_LOGS_FILE, logs);
    
    res.status(201).json(newLog);
  } catch (error) {
    res.status(500).json({ message: 'Server error', error: error.message });
  }
});

app.delete('/api/nutrition-logs/:id', authenticateToken, async (req, res) => {
  try {
    const logs = await readJsonFile(NUTRITION_LOGS_FILE);
    const logIndex = logs.findIndex(log => log.id === req.params.id && log.userId === req.user.userId);
    
    if (logIndex === -1) {
      return res.status(404).json({ message: 'Log entry not found' });
    }
    
    logs.splice(logIndex, 1);
    await writeJsonFile(NUTRITION_LOGS_FILE, logs);
    
    res.json({ message: 'Log entry deleted successfully' });
  } catch (error) {
    res.status(500).json({ message: 'Server error', error: error.message });
  }
});

// Meal planning routes
app.get('/api/meals', authenticateToken, async (req, res) => {
  try {
    const meals = await readJsonFile(MEALS_FILE);
    const userMeals = meals.filter(meal => 
      meal.userId === req.user.userId || 
      (req.user.role === 'coach' && meal.coachId === req.user.userId)
    );
    
    res.json(userMeals);
  } catch (error) {
    res.status(500).json({ message: 'Server error', error: error.message });
  }
});

app.post('/api/meals', authenticateToken, async (req, res) => {
  try {
    const { name, foods, targetUserId } = req.body;
    
    const meals = await readJsonFile(MEALS_FILE);
    const newMeal = {
      id: uuidv4(),
      name,
      foods,
      userId: targetUserId || req.user.userId,
      coachId: req.user.role === 'coach' ? req.user.userId : null,
      createdAt: new Date().toISOString()
    };
    
    meals.push(newMeal);
    await writeJsonFile(MEALS_FILE, meals);
    
    res.status(201).json(newMeal);
  } catch (error) {
    res.status(500).json({ message: 'Server error', error: error.message });
  }
});

// Coach dashboard routes
app.get('/api/coach/clients', authenticateToken, async (req, res) => {
  try {
    if (req.user.role !== 'coach') {
      return res.status(403).json({ message: 'Access denied' });
    }
    
    const users = await readJsonFile(USERS_FILE);
    const clients = users.filter(user => user.role === 'client').map(user => ({
      id: user.id,
      email: user.email,
      firstName: user.firstName,
      lastName: user.lastName,
      profile: user.profile,
      createdAt: user.createdAt
    }));
    
    res.json(clients);
  } catch (error) {
    res.status(500).json({ message: 'Server error', error: error.message });
  }
});

// Serve React app
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, '../client/build/index.html'));
});

// Initialize data and start server
initializeData().then(() => {
  app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
  });
}).catch(error => {
  console.error('Failed to initialize data:', error);
});