import streamlit as st


def inject_bootstrap():
    return st.markdown("""
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.0.0/dist/css/bootstrap.min.css" integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">
<script src="https://code.jquery.com/jquery-3.2.1.slim.min.js" integrity="sha384-KJ3o2DKtIkvYIK3UENzmM7KCkRr/rE9/Qpg6aAZGJwFDMVNA/GpGFF93hXpG5KkN" crossorigin="anonymous"></script>
<script src="https://cdn.jsdelivr.net/npm/popper.js@1.12.9/dist/umd/popper.min.js" integrity="sha384-ApNbgh9B+Y1QKtv3Rn7W3mgPxhU9K/ScQsAP7hUibX39j7fakFPskvXusvfa0b4Q" crossorigin="anonymous"></script>
<script src="https://cdn.jsdelivr.net/npm/bootstrap@4.0.0/dist/js/bootstrap.min.js" integrity="sha384-JZR6Spejh4U02d8jOt6vLEHfe/JQGiRRSQQxSfFWpi1MquVdAyjUar5+76PVCmYl" crossorigin="anonymous"></script>
    """, unsafe_allow_html=True)


def display_summary(text):
    return st.markdown(f"""
    <table>
    <tr>
        <th>Aspect</th>
        <th>Development Agreement 1</th>
        <th>Development Agreement 2</th>
    </tr>
    <tr>
        <td>Date</td>
        <td>February 11, 2020</td>
        <td>February 11, 2020</td>
    </tr>
    <tr>
        <td>Project Scope</td>
        <td>Describes collaboration between Pelican Delivers, Inc. and Seattle Software Developers to improve the Pelican Delivers software with various functionalities and online apps</td>
        <td>Describes a Software Development Agreement between Pelican Delivers, Inc. and Seattle Software Developers, Inc. for creating specific software applications for Pelican Delivery, Inc.</td>
    </tr>
    <tr>
        <td>Milestones</td>
        <td>Four milestones with specific completion dates and payment amounts</td>
        <td>No mention of milestones</td>
    </tr>
    <tr>
        <td>Search Mechanism</td>
        <td>Includes a detailed description of the search mechanism, dispensary selection, product purchase, payment systems, ID verification, and checkout process</td>
        <td>No mention of these details</td>
    </tr>
    <tr>
        <td>Intellectual Property</td>
        <td>No explicit mention of intellectual property</td>
        <td>Addresses intellectual property concerns</td>
    </tr>
    <tr>
        <td>Confidentiality and Non-Disclosure</td>
        <td>No explicit mention of confidentiality and non-disclosure</td>
        <td>Includes confidentiality and non-disclosure obligations</td>
    </tr>
    <tr>
        <td>Independence Contracting</td>
        <td>No explicit mention of independence contracting</td>
        <td>Defines the relationship between the parties as independent contractors</td>
    </tr>
    <tr>
        <td>Guarantees and Representations</td>
        <td>No explicit mention of guarantees and representations</td>
        <td>Includes guarantees and representations by the developer</td>
    </tr>
    <tr>
        <td>Indemnification</td>
        <td>No explicit mention of indemnification</td>
        <td>Includes indemnification obligations</td>
    </tr>
    <tr>
        <td>Non-Disparagement</td>
        <td>No explicit mention of non-disparagement</td>
        <td>Includes non-disparagement obligations</td>
    </tr>
    <tr>
        <td>Termination</td>
        <td>No explicit mention of termination</td>
        <td>Includes termination provisions</td>
    </tr>
</table>
    """, unsafe_allow_html=True)
