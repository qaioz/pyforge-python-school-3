# Project Idea

This is just a conceptual plan for the project. This might change gradually as the project progresses.

For the part that is already implemented, check out the CurrentProgress.md file.

## Introduction

We were recommended by **Yaroslav Korkodinov** to add models:  Patients, Doctors and Drugs to the database. 

I was thinking about comming up with a project idea that would also include the molecules crud, that I already
spent much time on, and resemble a real world scenario.

So I came up with a hospital system, that is particularly focused on the personalization of the treatment,

Patients can be prescribed with the most suitable drugs and each drug can be composed of the most 
suitable molecules.

Maybe this does not sound very scientific and realistic, but I think it's at least nice for practicing. 
I had to learn about hierarchies in sqlalchemy and complex relationships. Additionally project includes OAuth2, jwt, and role based access control.

## User Roles and Flows

### 1. Doctor

#### Registration Flow
1. **Fill Application Form:** Provide details such as email, password,  full name, experience, and other required information.
2. **Await Acceptance:** Wait until your account is reviewed and activated by hospital admins.
3. **Login:** Use the provided credentials to log into the system.

#### Seeing Patients
1. **Access Patient List:** View a list of all assigned patients.
2. **View Patient Details:** Access details for each patient (excluding  password).

#### Writing Prescriptions
1. **Select Patient:** Choose a patient for whom the prescription is to be written.
2. **Create Prescription:** Enter prescription details, including the drug (one drug per prescription) and other required fields.

#### Accepting Appointments
1. **View Appointments:** Access a list of all appointments.
2. **Accept Appointment:** See the details of the appointment and confirm it. Possibly change the time.

### 2. Patient

#### Registration Flow
1. **Fill Application Form:** Provide details such as email, password, full name, and medical history.
2. **Await Acceptance:** Wait until your account is reviewed and activated by hospital admins.
3. **Login:** Use the provided credentials to log into the system.

#### Seeing Prescriptions
1. **Access Prescriptions:** View all prescriptions that have been prescribed to the patient.

#### Seeing Appointments
1. **View Appointments:** Access past and current appointments in the hospital.

#### Requesting Appointments
1. **Submit Request:** Provide details about the appointment request, including complaints, additional text, and preferred time.

### 3. Hospital Admin

#### Registration Flow
1. **Registration by Superadmin:** Superadmin is responsible for creating hospital admin accounts.

#### Seeing Registration Requests
1. **Access Requests:** View registration requests from patients and doctors.

#### Registering a Doctor/Patient
1. **Review Request:** Examine the registration request from a specific doctor or patient.
2. **Activate users:** Activate the accounts of registration requests

#### Managing Doctors, Patients, and Appointments
1. Can view, update, and delete all the information related to doctors, patients, and appointments.


### 4. Lab Admin

#### Managing Molecules and Drugs
1. **Populate System:** Enter and manage information related to molecules and drugs in the system.
2. **Substructure Search:** Perform searches for molecules based on substructures.

## Models

### DATABASE MODELS

![db_hospital - public.png](..%2F..%2FDesktop%2Fdb_hospital%20-%20public.png)

#### 1. Base 

- **created_at:** DateTime, default=now
- **updated_at:** DateTime, default=now, onupdate=now

#### 2. Molecule

- **id:** Integer, primary_key
- **name:** String, nullable=False
- **smiles:** String, nullable=False

#### 3. Drug

- **id:** Integer, primary_key
- **name:** String, nullable=False
- **description:** Text
- **molecules:** Many-to-Many relationship with Molecule

#### 4. User

- **id:** Integer, primary_key
- **email:** String, nullable=False
- **password:** String, nullable=False
- **full_name:** String, nullable=False
- **is_active:** Boolean, default=True
- **role:** Enum, values=['doctor', 'patient', 'hospital_admin', 'lab_admin']


#### 5. Patient(User)

- **gender:** Enum
- **date_of_birth:** Date
- **Medical_history:** Text

- **user_id:** Integer, ForeignKey('user.id')
- **doctor:** Many-to-One relationship with Doctor
- **prescriptions:** One-to-Many relationship with Prescription
- **appointments:** One-to-Many relationship with Appointment

#### 6. Doctor(User)

- **specialization:** String
- **experience:** Integer
- **description:** Text

- **user_id:** Integer, ForeignKey('user.id')
- **patients:** One-to-Many relationship with Patient
- **appointments:** One-to-Many relationship with Appointment


#### 7. appointment

- **doctor_id:** Integer, ForeignKey("doctor")
- **patient_id:** Integer, ForeignKey("patient")
- **date:** DateTime
- **complaints:** Text
- **additional_text:** Text
- **status:** Enum, values=['pending', 'confirmed', 'completed', 'cancelled']

#### 8. Prescription

- **doctor_id:** Integer, ForeignKey("doctor")
- **patient_id:** Integer, ForeignKey("patient")
- **drug_id:** Integer, ForeignKey("drug")
- **date:** DateTime
- **description:** Text


## API Endpoints

### `api/molecules/`

This endpoint is for lab admins. It allows them to manage molecules in the system.

Maybe some functionalities can be exposed to curious people, who want to know what 
substances are there in the medices they consume, or maybe to learn more about molecules.

#### **for lab_admin**:

    - POST: Create a new molecule

    - DELETE: /{molecule_id} Delete a molecule by id

    - PUT: /{molecule_id} Update a molecule by id

    - POST: /upload Upload a csv file containing molecules info


#### **for everyone**:
    
    - GET: /{molecule_id} Get a molecule by id

    - GET: /?page={page}&page_size={page_size}?name={name} Get all molecules, you can filter by name

    - GET: /search/having_substructure?substructure={substructure_smiles} Get all molecules containing a given substructure

    - GET: /search/substructures?smiles={smiles} Get all substructures of a molecule

### `api/drugs/`
    
#### **for lab_admin**:

    - POST: Create a new drug

    - DELETE: /{drug_id} Delete a drug by id

    - PUT: /{drug_id} Update a drug by id

#### **for everyone**

    - GET: /?page={page}&page_size={page_size}?name={drug_name} Get all drugs, you can filter by name

    - GET: /{drug_id} Get a drug by id

### `api/patients/`

#### **for everyone**:
    
    - POST: Register

    - GET: /{patient_id}/public_profile Get a patient's public profile info
    
#### **for hospital_admin**:
    
    - GET: /{patient_id} Get a patient by id

    - DELETE: /{patient_id} Delete a patient by id

    - PUT: /{patient_id} Update a patient by id
    
    - PATCH: /{patient_id}/set_active 

#### **for patient**:
    
    - GET: /me get the patient's own profile
 
    - GET: /me/prescriptions get all prescriptions of the patient

    - GET: /me/appointments?status={status}get all appointments of the patient you can filter by status, default is pending

    - POST: /me/appointments request a new appointment

[//]: # (    - PATCH: me/appointments/{appointment_id} update appointment details   )

### `api/doctors/`

#### **for everyone**:
    
    - POST: Register

    - GET: /{doctor_id}/public_profile Get a doctor's public profile info

#### **for hospital_admin**:
    
    - GET: /{doctor_id} Get a doctor by id
    
    - GET: /?active={active} Get all doctors, you can see only active doctors if you filter by active=True

    - DELETE: /{doctor_id} Delete a doctor by id

    - PUT: /{doctor_id} Update a doctor by id
   
    - PATCH: /{doctor_id}/set_active  Activate or deactivate a doctor

#### **for doctor**:

    - GET: /me get the doctor's own profile

    - PATCH: /me update the doctor's own profile info including password, but not role
    
    - GET: /me/patients get all patients of the doctor

    - GET: /me/patients/{patient_id} get a patient of the doctor

    - POST: /me/patients/{patient_id}/prescriptions create a new prescription for a patient

[//]: # (    - PATCH: /me/patients/{patient_id}/prescriptions/{prescription_id} update a prescription for a patient)

    - GET: /me/appointments?status={status} get all appointments of the doctor, you can filter by status, default is pending


### `api/appointments/`

#### **for hospital_admin**:
    
    - GET: /{appointment_id} Get an appointment by id
    
    - GET: /?status={status} Get all appointments, you can filter by status

    - PUT: /{appointment_id} Update an appointment by id

    - DELETE: /{appointment_id} Delete an appointment by id


### `api/prescriptions/`

### **for hospital_admin**:

    - GET: /{prescription_id} Get a prescription by id
    
    - GET: /?doctor_id={doctor_id}&patient_id={patient_id} Get all prescriptions, you can filter by doctor_id and patient_id
    
    - PUT: /{prescription_id} Update a prescription by id
    
    - DELETE: /{prescription_id} Delete a prescription by id


### `api/users/`
    
#### **for lab_admin, hospital_admin, or superuser**:
    - GET: /me get the user's own profile

#### **for super_admin**

    - POST: Create a new user
     
    - GET: /{user_id} Get a user by id

    - GET: /?page={page}&page_size={page_size} Get all users
   
    - DELETE: /{user_id} Delete a user by id

    - PUT: /{user_id} Update a user by id


### `api/auth/`
   
#### **for everyone**

   - POST: /token
   

**for everyone**

    - POST: /token Get a jwt token

**for hospital_admin**
   
 


## DTOs

Let's define DTO classes for the API endpoints. 

If the field is not marked as nullable, it means that the field is required.

Api will comply to the HATEOAS principle, specifically JSON Hypermedia API Language (HAL), meaning
that the response will contain links to related resources in the response body.

Before defining the important DTOs, lets start with the Link, and HyperlinkResponse DTOs, to 
define the structure of the HAL response.

### Link

- **method:** str  GET, POST, PUT, DELETE
- **href:** str    The url of the resource
- **rel:** str     The relation of the resource to the current resource, e.g. self, next, patients, etc.

### HyperlinkResponse

- **links:** Dict[str, Link]   e.g. {"self": Link, "next": Link, "patients": Link}


### MoleculeRequest

- **name:** str
- **smiles:** str

**validation:** smiles should be a valid smiles string


### MoleculeResponse(HyperlinkResponse, MoleculeRequest)

- **id:** int
- **smiles:** int 
- **links:** Dict[str, Link]
   {"self": Link, "is_substructure_of": Link, "substructures": Link}


### DrugRequest

- **name:** str
- **description:** str
- **molecule_ids:** List[int]


### DrugResponse(HyperlinkResponse, DrugRequest)

- **id:** int
- **name:** str
- **description:** str
- **molecules_ids:** List[MoleculeResponse]
- **links:** Dict[str, Link]
   {"self": Link}


### UserRegistrationRequest

- **email:** str
- **password:** str
- **full_name:** str
- **role:** str

### PatientRegistrationRequest(UserRegistrationRequest)

- **gender:** str
- **date_of_birth:** date
- **medical_history:** str nullable
- **description:** str nullable

### RegistrationResponse

This is just a message to confirm that the user has been registered successfully.

- **message:** str  e.g. "User registration request has been submitted successfully. Please wait for approval."


### PatientUpdateRequest(PatientRegistrationRequest)

- every patient field 


### PatientSchedulingAppointmentRequest

- **preferred_time:** str
- **complaints:** str
- **additional_text:** str nullable


### PatientPublicProfileResponse

- **full_name:** str
- **gender:** str
- **date_of_birth:** str


### DoctorRegistrationRequest(UserRegistrationRequest)

- **specialization:** str
- **experience_years:** int
- **description:** str nullable


### DoctorPublicProfileResponse

- **full_name:** str
- **specialization:** str
- **experience_years:** int
- **description:** str nullable


### DoctorCreatingPrescriptionRequest

- **patient_id:** int
- **drug_id:** int
- **description:** str
- **date:** str

[//]: # (### DoctorUpdatingAppointmentRequest)

[//]: # ()
[//]: # (- **status:** str)

[//]: # (- **date:** str nullable)


[//]: # (### PatientUpdatingAppointmentRequest)

[//]: # ()
[//]: # (- **date:** str nullable)

[//]: # (- **complaints:** str nullable)

[//]: # (- **additional_text:** str nullable)

### AppointmentRequest

- **doctor_id:** int
- **patient_id:** int
- **date:** str
- **complaints:** str
- **additional_text:** str nullable
- **status:** str


### AppointmentResponse(HyperlinkResponse, AppointmentRequest)

- **id:** int
- **doctor_id:** int
- **patient_id:** int
- **date:** str
- **complaints:** str
- **additional_text:** str nullable
- **status:** str


### PrescriptionRequest

- **doctor_id:** int
- **patient_id:** int
- **drug_id:** int
- **description:** str

### PrescriptionResponse(HyperlinkResponse, PrescriptionRequest)

- **id:** int

### UserActivationRequest

- **set_is_active:** bool


### UserRequest

When updating a whole user, usually with higher roles

- **email:** str
- **password:** str
- **full_name:** str
- **role:** str
- **is_active:** bool


### UserResponse(HyperlinkResponse, UserRequest)

when getting a user, usually with higher roles

- **id:** int
- **email:** str
- **full_name:** str
- **role:** str
- **is_active:** bool
- **links:** Dict[str, Link]
   {"self": Link}









