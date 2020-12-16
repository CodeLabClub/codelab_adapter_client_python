'''
codelab-linda --monitor
codelab-linda --out [1, "hello"]
codelab-linda --rd [1, "*"]
codelab-linda --in [1, "hello"]
codelab-linda --dump

list 解析，json 输出，彩色
子命令

click, adapter full 已经内置 click
'''
import time
import click
import ast
from codelab_adapter_client import AdapterNode

class PythonLiteralOption(click.Option):
    def type_cast_value(self, ctx, value):
        try:
            return ast.literal_eval(value)
        except:
            raise click.BadParameter(value)

class CatchAllExceptions(click.Group):
    # https://stackoverflow.com/questions/44344940/python-click-subcommand-unified-error-handling
    def __call__(self, *args, **kwargs):
        try:
            return self.main(standalone_mode=False, *args, **kwargs)
        except Exception as exc:
            # click.echo(f'{args}, {kwargs}')
            mynode.terminate() # ok!

class MyNode(AdapterNode):
    NODE_ID = "eim/cli_linda_client"

    def __init__(self):
        super().__init__()

mynode = MyNode()
mynode.receive_loop_as_thread()
time.sleep(0.05)

@click.command()
@click.pass_obj
def dump(node):
    '''
    dump all tuples from Linda tuple space
    '''
    res = node.linda_dump()
    click.echo(res)
    return node

@click.command()
@click.option('-d', '--data', cls=PythonLiteralOption, default=[])
@click.pass_obj
def out(node, data):
    '''
    out the tuple to Linda tuple space
    '''
    # codelab-linda out --data '[1, "hello"]'
    
    assert isinstance(data, list)
    res = node.linda_out(data)
    click.echo(res)
    return node

@click.command("in")
@click.option('-d', '--data', cls=PythonLiteralOption, default=[])
@click.pass_obj
def in_(node, data): # replace
    '''
    in the tuple to Linda tuple space
    '''
    # codelab-linda in --data '[1, "*"]'
    
    assert isinstance(data, list)
    res = node.linda_in(data)
    click.echo(res)
    return node

@click.command("inp")
@click.option('-d', '--data', cls=PythonLiteralOption, default=[])
@click.pass_obj
def inp(node, data): # replace
    '''
    inp(in but Non-blocking) the tuple to Linda tuple space
    '''
    # codelab-linda in --data '[1, "*"]'
    
    assert isinstance(data, list)
    res = node.linda_inp(data)
    click.echo(res)
    return node

@click.group(cls=CatchAllExceptions)
@click.pass_context
def cli(ctx):
    '''
    talk with linda from cli
    '''
    ctx.obj = mynode


@cli.resultcallback()
def process_result(result, **kwargs):
    # click.echo(f'After command: {result} {kwargs}')
    # result is node
    if result._running:
        result.terminate()


cli.add_command(dump)
cli.add_command(out)
cli.add_command(in_)
cli.add_command(inp)
# 不阻塞一直跑