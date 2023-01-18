import React, { useRef, useState } from "react"
import { Form, Button, Card, Alert } from "react-bootstrap"
import { Link } from "react-router-dom"
import axios from "axios"
import { useNavigate } from "react-router-dom"

export default function Login() {
    const emailRef = useRef()
    const passwordRef = useRef()
    const [error, setError] = useState("")
    const [loading, setLoading] = useState(false)
    const navigate = useNavigate();

    async function handleSubmit(e) {
        e.preventDefault()
        axios.defaults.withCredentials = true;
        axios.post("http://localhost:5000/login", {
            password: passwordRef.current.value,
            email_address: emailRef.current.value
        }, {
            withCredentials: true
        })
            .then(res => {
                console.log(res);
                localStorage.setItem("email", emailRef.current.value)
                navigate('/films');
            })
            .catch(err => {
                console.log(err);
            });

        setLoading(false)
    }

    return (
        <>
            <div style={{paddingRight: "10%", paddingLeft:"10%", paddingTop:"10%", paddingBottom:"10%"}}>
                <Card class="mx-auto">
                    <Card.Body>
                        <h2 className="text-center mb-4">Log In</h2>
                        {error && <Alert variant="danger">{error}</Alert>}
                        <Form onSubmit={handleSubmit}>
                            <Form.Group id="email">
                                <Form.Label>Email</Form.Label>
                                <Form.Control type="email" ref={emailRef} required />
                            </Form.Group>
                            <Form.Group id="password">
                                <Form.Label>Password</Form.Label>
                                <Form.Control type="password" ref={passwordRef} required />
                            </Form.Group>
                            <br></br>
                            <Button disabled={loading} className="w-100" type="submit">
                                Log In
                            </Button>
                        </Form>
                        <div className="w-100 text-center mt-3">
                            <Link to="/forgot-password">Forgot Password?</Link>
                        </div>
                    </Card.Body>
                </Card>
                <div style={{color:"#adbac7"}} className="w-100 text-center mt-2">
                    Need an account? <Link style={{color:"#adbac7"}} to="/signup">Sign Up</Link>
                </div>
                <div className="w-100 text-center mt-2">
                    <Link style={{color:"#adbac7"}} to="/">Home</Link>
                </div>
            </div>
        </>
    )
}