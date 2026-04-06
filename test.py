import os
import subprocess

def remove_file(filename):
    if(os.path.exists(filename)):
        os.remove(filename)

def run_script(commands,filename="test.db"):
    remove_file("test.db")
    result=subprocess.run(   
            ["./a.out",filename,"--test-mode"],
            input = "\n".join(commands)+"\n",
            capture_output=True,
            text = True
            )
    return result.stdout.strip().split("\n")

def test_inserts_and_retrieve():
    output = run_script(["insert 1 user1 example.com","select",".exit"])
    expected_output = ["Executed.","(1 user1 example.com)","Executed."]
    assert (len(output)==len(expected_output))
    for i,o in enumerate(expected_output):
        assert o==expected_output[i]

def test_table_full():
    input = [f'insert {i} user{i} user{i}.com' for i in range(1500)]
    output = run_script(input)
    assert "Table full" in output 

def test_insert_max_length_string():
    username = "a"*32
    email = "b"*255
    input = [f'insert 1 {username} {email}',"select",".exit"]
    expected_output = ["Executed.",f'(1, {username}, {email})',"Executed."]
    output = run_script(input)
    assert(len(output)==len(expected_output))
    assert output==expected_output

def test_long_length_string():
    username = "a"*33
    email = "b"*256
    input = [f'insert 1 {username} {email}',"select",".exit"]
    expected_output = ["String is too long.","Executed."]
    output = run_script(input)
    assert output==expected_output

def test_ID_Negative():
    input = ["insert -1 user1 user1.com","select",".exit"]
    expected_output = ["ID must be positive.","Executed."]
    output = run_script(input)
    assert output==expected_output

def test_disk_persistence():
    result1 = run_script(["insert 1 user1 user1.com",".exit"],filename="test_disk.db")
    expected_result1 = ["Executed."]

    assert result1==expected_result1

    result2 = run_script(["select",".exit"],filename="test_disk.db")
    expected_result2 = ["(1, user1, user1.com)","Executed."]

    assert result2==expected_result2

    remove_file("test_disk.db")

def test_btree():
    input1 = [f'insert {i} user{i} user{i}.com' for i in range(3)] + [".btree"] + ['.exit']
    output1 = run_script(input1);
    expected_output1 = ["Executed.","Executed.","Executed.","Tree:","leaf (size 3)","  - 0 : 0","  - 1 : 1","  - 2 : 2"]
    assert output1 == expected_output1

def test_duplicate_keys():
    input = ["insert 1 user1 user1.com","insert 1 user1 user1.com","select",".exit"]
    output = run_script(input)
    expected_output = ["Executed.","Error: Duplicate Key.","(1, user1, user1.com)","Executed."]
    assert output==expected_output
