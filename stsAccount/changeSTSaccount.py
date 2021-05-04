
def changeSTSAccount(sts, accountId, rolename):
    assumed_role_object=sts.assume_role(
        RoleArn="arn:aws:iam::"+accountId+":role/"+rolename,
        RoleSessionName="AssumeRoleSession1"
    )
    # print(assumed_role_object)
    return assumed_role_object
