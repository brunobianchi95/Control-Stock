import { useState, useEffect } from "react";
import type { NextPage } from "next";
import Head from "next/head";
import Image from "next/image";
import styles from "../styles/Home.module.css";
import useSWR from "swr";

const baseUrl = "http://localhost:5000";

const Login = (props: { onLogin: (token: string) => void }) => {
  const [email, setEmail] = useState("bianchi.b95@gmail.com");
  const [password, setPassword] = useState("catalina");
  const login = async () => {
    const response = await fetch(baseUrl + "/api/login", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        email,
        password,
      }),
    });
    const json = await response.json();
    props.onLogin(json.token);
    console.log(json);
  };

  return (
    <div>
      <h2>Login</h2>
      <input
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder="Email"
      />
      <input
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        placeholder="Password"
      />
      <button onClick={login}>Login</button>
    </div>
  );
};

const Signup = () => {
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const signup = async () => {
    const response = await fetch(baseUrl + "/api/login", {
      method: "POST",
      body: JSON.stringify({
        firstName,
        lastName,
        email,
        password,
      }),
    });
    const json = await response.json();
    console.log(json);
  };
  return (
    <div>
      <h2>Signup</h2>
      <input
        value={firstName}
        onChange={(e) => setFirstName(e.target.value)}
        placeholder="First name"
      />
      <input
        value={lastName}
        onChange={(e) => setLastName(e.target.value)}
        placeholder="Last name"
      />
      <input
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder="Email"
      />
      <input
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        placeholder="Password"
      />
      <button onClick={signup}>Signup</button>
    </div>
  );
};

type Message = {
  message_id: number;
  message: string;
  sender_id: number;
  receiver_id: number;
  is_read: boolean;
};

const Chat = (props: { token: string; user: User }) => {
  const [messages, setMessages] = useState<Array<Message>>([]);

  const [composer, setComposer] = useState("");

  const fetchMessages = async () => {
    const response = await fetch(baseUrl + "/api/messages", {
      method: "GET",
      headers: {
        "content-type": "application/json",
        authorization: props.token,
      },
    });

    if (response.status !== 200) {
      console.log("fallo");
    }

    const messages = await response.json();
    setMessages(messages);
  };

  const sendMessage = async () => {
    const response = await fetch(baseUrl + "/api/messages", {
      method: "POST",
      headers: {
        "content-type": "application/json",
        authorization: props.token,
      },
      body: JSON.stringify({
        message: composer,
        receiver_id: props.user.user_id,
      }),
    });

    if (response.status !== 200) {
      console.log("fallo");
    }

    const jsonMessage = await response.json();
    setMessages([...messages, jsonMessage]);
    setComposer("");
  };

  useEffect(() => {
    fetchMessages();
    const timer = setInterval(() => fetchMessages(), 1000);
    return () => clearInterval(timer);
  }, []);

  return (
    <div>
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          width: 500,
          height: 500,
          overflowY: "scroll",
        }}
      >
        {messages.map((message) => {
          return (
            <div
              key={message.message_id}
              style={{
                alignSelf:
                  props.user.user_id === message.sender_id
                    ? "flex-start"
                    : "flex-end",
                margin: 16,
              }}
            >
              {message.message}
            </div>
          );
        })}
      </div>

      <input
        placeholder="Escribi el mensaje capo"
        value={composer}
        onChange={(e) => setComposer(e.target.value)}
        onKeyDown={(k) => {
          if (k.keyCode === 13) {
            sendMessage();
          }
        }}
      />
      <button
        onClick={() => {
          sendMessage;
        }}
      >
        Enviar mensajes
      </button>
      <br />
      <button onClick={fetchMessages}>Recargar chat</button>
    </div>
  );
};

type User = {
  user_id: number;
  first_name: string;
  last_name: string;
  email: string;
};

const fetcher = (url: string) =>
  fetch(baseUrl + url, {
    headers: {
      "content-type": "application/json",
      authorization: localStorage.getItem("token") || "",
    },
  }).then((r) => r.json());

const Home: NextPage = () => {
  const [token, setToken] = useState<string | null>(
    typeof window !== "undefined" ? localStorage.getItem("token") : null
  );

  const [chatUser, setChatUser] = useState<number | null>(null);

  const [users, setUsers] = useState<Array<User>>([]);

  const fetchUsers = async (token: string) => {
    const response = await fetch(baseUrl + "/api/messages/users", {
      method: "GET",
      headers: {
        "content-type": "application/json",
        authorization: token,
      },
    });

    if (response.status !== 200) {
      console.log("fallo");
    }

    const users = await response.json();
    setUsers(users);
  };

  useEffect(() => {
    if (token) {
      fetchUsers(token);
    }
  }, []);

  if (token === null) {
    return (
      <Login
        onLogin={(token) => {
          localStorage?.setItem("token", token);
          setToken(token);
        }}
      />
    );
  }

  const selectedUser = users.find((u) => u.user_id === chatUser);
  return (
    <div>
      <h2>Estas logeado master</h2>

      <h3>Chatear con usuario</h3>
      <ul>
        {users?.map((user) => (
          <li key={user.user_id} onClick={() => setChatUser(user.user_id)}>
            {user.first_name}
          </li>
        ))}
      </ul>

      {selectedUser && (
        <>
          <h2>Hablando con {selectedUser.first_name}</h2>
          <Chat token={token} user={selectedUser} />
        </>
      )}
    </div>
  );
};

export default Home;
