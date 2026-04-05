from flask import Flask, render_template, request, jsonify
import pickle
import os

app = Flask(__name__)

model_path = os.path.join(os.path.dirname(__file__), 'model', 'model.pkl')
with open(model_path, 'rb') as f:
    model_data = pickle.load(f)
    model = model_data['model']
    raw_symptoms = model_data['symptoms']

clean_symptoms = []
for sym in raw_symptoms:
    clean_name = sym.replace('_', ' ').strip().title()
    clean_symptoms.append({'id': sym, 'name': clean_name})

clean_symptoms = sorted(clean_symptoms, key=lambda x: x['name'])

# --- NEW: Recommendations Dictionary ---
precautions_dict = {
    "Fungal infection": ["Keep the affected area clean and dry.", "Apply prescribed anti-fungal cream.", "Wear loose-fitting, breathable clothes.", "Do not share personal towels."],
    "Allergy": ["Avoid exposure to known allergens.", "Keep your environment dust-free.", "Use air purifiers at home.", "Take antihistamines if prescribed."],
    "GERD": ["Avoid spicy, acidic, and fatty foods.", "Eat smaller, more frequent meals.", "Do not lie down immediately after eating.", "Elevate the head of your bed."],
    "Migraine": ["Rest in a dark, quiet room.", "Apply a cold compress to your forehead.", "Stay hydrated.", "Avoid loud noises and strong smells."],
    "Malaria": ["Consult a doctor immediately for blood tests.", "Take prescribed antimalarial drugs.", "Rest and drink plenty of fluids.", "Use mosquito nets to prevent further bites."],
    "Chicken pox": ["Avoid scratching blisters to prevent scarring.", "Take oatmeal baths to relieve itching.", "Isolate to prevent spreading.", "Stay hydrated and rest."],
    "Dengue": ["Drink plenty of fluids (water, coconut water).", "Take Paracetamol for fever (Avoid Aspirin/Ibuprofen).", "Monitor platelet count regularly.", "Rest completely."],
    "Typhoid": ["Complete the full course of prescribed antibiotics.", "Drink boiled or purified water.", "Eat light, easily digestible food.", "Wash hands thoroughly before eating."],
    "Acne": ["Wash your face twice daily with a gentle cleanser.", "Avoid popping or squeezing pimples.", "Use non-comedogenic skincare products.", "Drink plenty of water."],
    "Common Cold": ["Rest and stay warm.", "Drink warm fluids like soup or herbal tea.", "Gargle with warm salt water.", "Use a humidifier to ease congestion."]
}
# Default recommendation if disease isn't in the dictionary
default_recs = ["Please consult a healthcare professional for accurate advice.", "Get plenty of rest.", "Stay hydrated.", "Monitor your symptoms closely."]

@app.route('/')
def home():
    return render_template('index.html', symptoms=clean_symptoms)

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        user_symptoms = data.get('symptoms', [])

        input_data = [0] * len(raw_symptoms)
        for symptom in user_symptoms:
            if symptom in raw_symptoms:
                index = raw_symptoms.index(symptom)
                input_data[index] = 1

        prediction = model.predict([input_data])[0]
        
        # --- NEW: Get recommendations for the predicted disease ---
        recs = precautions_dict.get(prediction, default_recs)

        return jsonify({
            'success': True, 
            'disease': prediction.title(),
            'recommendations': recs # Send recommendations to frontend
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)