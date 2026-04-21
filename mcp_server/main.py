from server import mcp

# We are importing them for their side effect:
# when Python imports these modules, the @mcp.tool() decorators run and register the tools on the MCP server.
import tools.drukair
import tools.bhutan_telecom

if __name__=="__main__":
    mcp.run()