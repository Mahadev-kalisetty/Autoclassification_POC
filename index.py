import os
from flask import Flask,request, abort, jsonify, send_from_directory
from flask_restful import Api
import pandas as pd
import json
from io import BytesIO
import numpy as np

UPLOAD_DIRECTORY = "api_uploaded_files"

process_status=0    
if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)


api = Flask(__name__)
api.secret_key = "super secret key"
api2 = Api(api)

@api.route("/files")
def list_files():
    """Endpoint to list files on the server."""
    files = []
    for filename in os.listdir(UPLOAD_DIRECTORY):
        path = os.path.join(UPLOAD_DIRECTORY, filename)
        if os.path.isfile(path):
            files.append(filename)
    return jsonify(files)

@api.route("/files/<path:path>")
def get_file(path):
    """Download a file."""
    return send_from_directory(UPLOAD_DIRECTORY, path, as_attachment=True)

@api.route("/checkscorecalculationstatus/<filename>", methods=["GET"])
def checkscorecalculationprogress(filename):
 print('Global value in get',process_status)
 return str(process_status)

@api.route("/files/<filename>", methods=["POST"])
def post_file(filename):
    """Upload a file."""
   
    if "/" in filename:
        # Return 400 BAD REQUEST
        abort(400, "no subdirectories allowed")

    #with open(os.path.join(UPLOAD_DIRECTORY, filename), "wb") as fp:
        #fp.write(request.data)
    rr = request.data
    df = pd.read_csv(BytesIO(rr))
    print(df)
   
    class NpEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, np.integer):
                return int(obj)
            if isinstance(obj, np.floating):
                return float(obj)
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            return super(NpEncoder, self).default(obj)
       
    update_list = []
    totalUniqueCount=0
    totalCount=0
    for column in df:
        unique_percentage = df[column].value_counts(normalize=True)*100
        print("gpn log is ",unique_percentage)
        totalUniqueCount=totalUniqueCount+df[column].nunique()
        print("totalUniqueCount is ",totalUniqueCount)
        totalCount=totalCount+df[column].count()
        print("totalCount is ",totalCount)
        remCount=totalCount-totalUniqueCount
        print("remCount is : ",remCount)
        pct = float(remCount/totalCount) * 100
        print("pct is : ",pct)
        totalPercentage =round(pct, 2)
        print("totalPercentage is : ",totalPercentage)
        print(column)
        print(df[column].nunique())
        print(df[column].count())
        if(totalPercentage<5.00):
            data_set ={"column": column, "Number of unique values": df[column].nunique(), "Total number of Non Null Rows": df[column].count()}
            print(data_set)
            update_list.append(data_set)
            pp={"Potential Dictionaries": update_list}
    print(pp)
    to_json = json.dumps(pp, cls=NpEncoder)
    print(to_json)

    # Return 201 CREATED
    return  to_json,201


#api2.add_resource(AutoClass, "/autoclass/cl")

if __name__ == "__main__":
  api.run()