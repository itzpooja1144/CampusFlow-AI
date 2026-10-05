def predict_crowd_risk(current_occupancy, capacity):

    try:
        # Make sure values are numeric
        current_occupancy = int(current_occupancy or 0)
        capacity = int(capacity or 0)

        now = datetime.now()

        hour = int(now.hour)
        day_of_week = int(now.weekday())

        if capacity > 0:
            occupancy_ratio = float(current_occupancy / capacity)
        else:
            occupancy_ratio = 0.0

        # EXACT features used while training Logistic Regression
        input_data = pd.DataFrame([{
            "current_occupancy": current_occupancy,
            "capacity": capacity,
            "occupancy_ratio": occupancy_ratio,
            "hour": hour,
            "day_of_week": day_of_week
        }])

        print("\n-----------------------------")
        print("LOGISTIC INPUT")
        print(input_data)
        print("-----------------------------")

        # Prediction
        prediction = int(logistic_model.predict(input_data)[0])

        # Probability
        probability = 0.0

        if hasattr(logistic_model, "predict_proba"):

            probabilities = logistic_model.predict_proba(input_data)[0]

            classes = list(logistic_model.classes_)

            if 1 in classes:
                risk_index = classes.index(1)
                probability = float(probabilities[risk_index]) * 100

        probability = round(probability, 2)

        # Status
        if prediction == 1:
            status = "OVERCROWDING RISK"
        else:
            status = "SAFE"

        return {
            "status": status,
            "probability": probability,
            "prediction": prediction,
            "error": None
        }

    except Exception as e:

        print("\n==============================")
        print("LOGISTIC MODEL ERROR")
        print("==============================")
        print(str(e))
        print("==============================")

        return {
            "status": "Prediction Error",
            "probability": 0,
            "prediction": 0,
            "error": str(e)
        }