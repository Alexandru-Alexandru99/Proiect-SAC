import React, { useRef, useState } from "react"
import { Form, Button, Card, Alert } from "react-bootstrap"
import { Link } from "react-router-dom"

export default function ForgotPassword() {
    const emailRef = useRef()
    const [error, setError] = useState("")
    const [message, setMessage] = useState("")
    const [loading, setLoading] = useState(false)

    async function handleSubmit(e) {
        e.preventDefault()

        console.log("Forgot password")

        setLoading(false)
    }

    return (
        <>
            <div style={{ paddingRight: "10%", paddingLeft: "10%", paddingTop: "10%", paddingBottom: "10%" }}>

                <Card>
                    <Card.Body>
                        <h2 className="text-center mb-4">Password Reset</h2>
                        {error && <Alert variant="danger">{error}</Alert>}
                        {message && <Alert variant="success">{message}</Alert>}
                        <Form onSubmit={handleSubmit}>
                            <Form.Group id="email">
                                <Form.Label>Email</Form.Label>
                                <Form.Control type="email" ref={emailRef} required />
                            </Form.Group>
                            <br></br>
                            <Button disabled={loading} className="w-100" type="submit">
                                Reset Password
                            </Button>
                        </Form>
                        <div className="w-100 text-center mt-3">
                            <Link to="/login">Login</Link>
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