import React, { useRef, useState } from "react"
import { Form, Button, Card, Alert } from "react-bootstrap"
import { Link } from "react-router-dom"
import axios from "axios"
import { useNavigate } from "react-router-dom"

export default function Signup() {
    const emailRef = useRef()
    const passwordRef = useRef()
    const passwordConfirmRef = useRef()
    const ageRef = useRef()
    const firstnameRef = useRef()
    const lastnameRef = useRef()
    const genderRef = useRef()
    const film1Ref = useRef()
    const film2Ref = useRef()
    const film3Ref = useRef()
    const filmtype1Ref = useRef()
    const filmtype2Ref = useRef()
    const filmtype3Ref = useRef()

    const [error, setError] = useState("")
    const [loading, setLoading] = useState(false)
    const navigate = useNavigate();

    async function handleSubmit(e) {
        e.preventDefault()
        axios.post("http://localhost:5000/signup", {
            password: passwordRef.current.value,
            email_address: emailRef.current.value,
            first_name: firstnameRef.current.value,
            last_name: lastnameRef.current.value,
            age: ageRef.current.value,
            gender: genderRef.current.value,
            films: [film1Ref.current.value, film2Ref.current.value, film3Ref.current.value],
            film_types: [filmtype1Ref.current.value, filmtype2Ref.current.value, filmtype3Ref.current.value]
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
            <div style={{ paddingRight: "10%", paddingLeft: "10%", paddingTop: "10%", paddingBottom: "10%" }}>

                <Card>
                    <Card.Body>
                        <h2 className="text-center mb-4">Sign Up</h2>
                        {error && <Alert variant="danger">{error}</Alert>}
                        <Form onSubmit={handleSubmit}>
                            <Form.Group id="firstname">
                                <Form.Label>First name</Form.Label>
                                <Form.Control type="text" ref={firstnameRef} required />
                            </Form.Group>
                            <Form.Group id="lastname">
                                <Form.Label>Last name</Form.Label>
                                <Form.Control type="text" ref={lastnameRef} required />
                            </Form.Group>
                            <Form.Group id="age">
                                <Form.Label>Age</Form.Label>
                                <Form.Control type="number" ref={ageRef} required />
                            </Form.Group>
                            <Form.Group id="gender">
                                <Form.Label>Gender</Form.Label>
                                <Form.Control type="text" ref={genderRef} required />
                            </Form.Group>
                            <Form.Group id="film1">
                                <Form.Label>Film 1</Form.Label>
                                <Form.Control type="text" ref={film1Ref} required />
                            </Form.Group>
                            <Form.Group id="film2">
                                <Form.Label>Film 2</Form.Label>
                                <Form.Control type="text" ref={film2Ref} required />
                            </Form.Group>
                            <Form.Group id="film3">
                                <Form.Label>Film 3</Form.Label>
                                <Form.Control type="text" ref={film3Ref} required />
                            </Form.Group>
                            <Form.Group id="filmtype1">
                                <Form.Label>Film type 1</Form.Label>
                                <Form.Control type="text" ref={filmtype1Ref} required />
                            </Form.Group>
                            <Form.Group id="filmtype2">
                                <Form.Label>Film type 2</Form.Label>
                                <Form.Control type="text" ref={filmtype2Ref} required />
                            </Form.Group>
                            <Form.Group id="filmtype3">
                                <Form.Label>Film type 3</Form.Label>
                                <Form.Control type="text" ref={filmtype3Ref} required />
                            </Form.Group>
                            <Form.Group id="email">
                                <Form.Label>Email</Form.Label>
                                <Form.Control type="email" ref={emailRef} required />
                            </Form.Group>
                            <Form.Group id="password">
                                <Form.Label>Password</Form.Label>
                                <Form.Control type="password" ref={passwordRef} required />
                            </Form.Group>
                            <Form.Group id="password-confirm">
                                <Form.Label>Password Confirmation</Form.Label>
                                <Form.Control type="password" ref={passwordConfirmRef} required />
                            </Form.Group>
                            <br></br>
                            <Button disabled={loading} className="w-100" type="submit">
                                Sign Up
                            </Button>
                        </Form>
                    </Card.Body>
                </Card>
                <div style={{color:"#adbac7"}} className="w-100 text-center mt-2">
                    Already have an account? <Link style={{color:"#adbac7"}} to="/login">Log In</Link>
                </div>
                <div className="w-100 text-center mt-2">
                    <Link style={{color:"#adbac7"}} to="/">Home</Link>
                </div>
            </div>
        </>
    )
}