/**
 * Copyright 2015 Google Inc. All Rights Reserved.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
'use strict';

$(document).ready(() => {
    $('#sign-in').on('click', () => {
        var provider = new firebase.auth.GoogleAuthProvider();
        firebase.auth().signInWithPopup(provider).catch(err => console.log(err));
    });

    $('#sign-out').on('click', () => {
        firebase.auth().signOut();
    });

    firebase.auth().onAuthStateChanged(user => {
        if (user) { // User is signed in!
            var profiles_db = firebase.firestore().collection('profiles');

            profiles_db.doc(user.uid).get().then(profile => {
                if (profile.exists) {
                    console.log("uhul");
                } else {
                    profiles_db.doc(user.uid).set({
                        role: 'host',
                    });
                }
            }).catch(err => console.log(err));
        } else { // User is signed out!

        }
    });
})

// Returns the signed-in user's profile Pic URL.
function getProfilePicUrl() {
    return firebase.auth().currentUser.photoURL || '/images/profile_placeholder.png';
}

// Returns the signed-in user's display name.
function getUserName() {
    return firebase.auth().currentUser.displayName;
}

// Returns true if a user is signed-in.
function isUserSignedIn() {
    return !!firebase.auth().currentUser;
}
