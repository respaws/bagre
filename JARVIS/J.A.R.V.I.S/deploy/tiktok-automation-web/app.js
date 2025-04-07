const express = require("express");
const app = express();

const users = {
  bagre: "91980514xx"
};

app.use(express.json());

app.post("/login", (req, res) => {
  const { username, password } = req.body;
  if (users[username] && users[username] === password) {
    return res.json({ message: "Login OK", user: username });
  }
  return res.status(401).json({ error: "Login inválido" });
});

app.listen(3000, () => console.log("Servidor rodando na porta 3000"));
