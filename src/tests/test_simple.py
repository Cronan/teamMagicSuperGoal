import teammagicsupergoal.utils as magic_utils


def test_one():
    assert 'teammagicsupergoal/data/example.csv' in magic_utils.get_data_path('example.csv')
