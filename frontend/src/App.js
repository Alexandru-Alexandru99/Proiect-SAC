import React from "react"
import { Container } from "react-bootstrap"
import { BrowserRouter, Routes, Route } from "react-router-dom"
import Login from "./components/Login"
import ForgotPassword from "./components/ForgotPassword"
import Signup from "./components/Signup"
import Films from "./components/Films"
import Home from "./components/Home"
import Profile from "./components/Profile"

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route exact path='/' element={<Home/>}></Route>
        <Route path='/signup' element={<Signup/>}></Route>
        <Route path='/login' element={<Login/>}></Route>
        <Route path='/forgot-password' element={<ForgotPassword/>}></Route>
        <Route path='/films' element={<Films/>}></Route>
        <Route path='/profile' element={<Profile/>}></Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App