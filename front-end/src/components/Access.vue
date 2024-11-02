<script setup>
    import { Form, Field, ErrorMessage } from 'vee-validate'
    import { object, string } from "yup"
    import { useIdentityStore } from '@/stores/identity.js'
    import { useAlertStore } from '@/stores/alert.js'
    import { fetchfunct, checkerror } from './fetch.js'
    import router from '../router/index.js'

    const props = defineProps( [ 'access' ] )

    const login_schema = object().shape( {
        username: string().trim().matches( /^[\p{L}\p{N}]+$/u, "Must be unicode letters and numbers only." ).required().min( 4 ).max( 32 ).strict(),
        password: string().matches( /^(?!(^\s+$))/, 'Blank-spaces only password is not allowed.' ).required().min( 8 ).strict(),
    } )

    async function login ( values, { resetForm } )
    {

        // hiding the bootstrap modal element
        bootstrap.Modal.getInstance( "#accessModal" ).hide()
        //resetting the form
        resetForm()
        //sending the login details
        let headersList = {
            "Content-Type": "application/json"
        }

        let bodyContent = JSON.stringify( {
            "username": values.username,
            "password": values.password,
        } )


        let response = await fetchfunct( "login?include_auth_token", { method: "POST", body: bodyContent, headers: headersList } )

        if ( response.ok )
        {
            //getting the user role
            let data = await response.json()
            localStorage.setItem( "Authentication-Token", data.response.user.authentication_token )

            let r = await fetchfunct( "user/role" )
            if ( r.ok )
            {
                useIdentityStore().identity = await r.json()
                localStorage.setItem( "Identity", JSON.stringify( useIdentityStore().identity ) )
                useAlertStore().alertpush( [ { msg: 'You have successfully logged in!', type: 'alert-success' } ] )
            }
            else
            {
                checkerror( r )
            }
        }
        else
        {
            checkerror( response )
        }
    }

    async function logout ()
    {
        // hiding the bootstrap modal element
        bootstrap.Modal.getInstance( "#accessModal" ).hide()

        let r = await fetchfunct( "logout" )
        if ( r.ok || r.status == 401 )
        {   // logout is successfully or the authentication token has expired
            localStorage.removeItem( 'Authentication-Token' )
            localStorage.removeItem( 'Identity' )
            useIdentityStore().identity = [ 'Unauthenticated' ]
            router.push( '/' )
            useAlertStore().alertpush( [ { msg: 'You have successfully logged out!', type: 'alert-success' } ] )
        }
        else
        {
            checkerror( r )
        }
    }

</script>

<template>
    <div class="modal fade" id="accessModal" tabindex="-1">
        <div class="modal-dialog modal-dialog-scrollable">
            <div class="modal-content">
                <div class="modal-header">
                    <h1 class="modal-title fs-5">
                        <b>{{access}}</b>
                    </h1>
                    <button class="btn btn-outline-danger" data-bs-dismiss="modal"><i class="bi bi-x-lg"></i></button>
                </div>

                <div class="modal-body">
                    <div v-if="access=='Logout'">
                        <div class="mb-3">Do you want to logout?</div>
                        <div class='d-grid gap-2'>
                            <button class="btn btn-outline-primary" @click="logout">Confirm</button>
                        </div>
                    </div>
                    <div v-else>
                        <Form @submit="login" :validation-schema="login_schema">
                            <div class="form-floating mb-3 form-element">
                                <Field name="username" autocomplete='username' placeholder='username'
                                    class="form-control"></Field>
                                <label>Username</label>
                                <ErrorMessage class="form-text" name="username"></ErrorMessage>
                            </div>
                            <div class="form-floating mb-3 form-element">
                                <Field name="password" type="password" autocomplete='current-password'
                                    placeholder='password' class="form-control"></Field>
                                <label>Password</label>
                                <ErrorMessage class="form-text" name="password"></ErrorMessage>
                            </div>
                            <div class='d-grid gap-2'>
                                <button class='btn btn-outline-primary'>Login</button>
                            </div>
                        </Form>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>