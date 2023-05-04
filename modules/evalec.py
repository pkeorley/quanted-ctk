import ast


def insert_returns(body):
    if isinstance(body[-1], ast.Expr):
        body[-1] = ast.Return(body[-1].value)
        ast.fix_missing_locations(body[-1])
        if isinstance(body[-1], ast.If):
            insert_returns(body[-1].body)
            insert_returns(body[-1].orelse)
        if isinstance(body[-1], ast.With):
            insert_returns(body[-1].body)


async def execute_code(code, env: dict = None):
    fn_name = "_eval_expr"
    cmd = "\n".join(f" {i}" for i in code.splitlines())
    body = f"async def {fn_name}():\n{cmd}"
    parsed = ast.parse(body)
    body = parsed.body[0].body
    insert_returns(body)
    env = {'__import__': __import__, **env}
    exec(compile(parsed, filename="<ast>", mode="exec"), env)
    result = (await eval(f"{fn_name}()", env))
    return result
