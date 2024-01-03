const express = require('express');
const { CognosAPI } = require('./api.js');
require('dotenv').config();


const app = express ();
const PORT = 3000;

app.use(express.json());
process.env['NODE_TLS_REJECT_UNAUTHORIZED'] = 0; // MUST BE REMOVED FOR PRODUCTION

const CA = new CognosAPI(process.env.API_URL);
console.log('Logging in to Cognos Analytics');
CA.login(process.env.API_USER, process.env.API_PASS, process.env.NAMESPACE);
console.log(`Logged in to Cognos Analytics as ${process.env.API_USER}`);
/****************** TODO ******************/
/* Logic to re-login when session expires */
/******************************************/

app.get('/get_reports', async (req, res) => {
  try {
    const data = await CA.get_reports(req.query.folder_id);
    res.send(data);
  } catch(e) {
    res.sendStatus(e);
  }
});


app.get('/get_permissions', async (req, res) => {
  try {
    const permissions = await CA.get_permissions(req.query.folder_id);
    res.send(permissions);
  } catch (e) {
    res.sendStatus(e);
  }
});


app.listen(PORT, () => {
  console.log('Server Listening on PORT:', PORT);
});
